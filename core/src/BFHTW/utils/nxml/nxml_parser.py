from typing import Dict, Optional, List, Generator
from lxml import etree
from uuid import uuid4
from datetime import datetime
from transformers import AutoTokenizer

from BFHTW.models.meta_model import MetaBase
from BFHTW.models.block_model import BlockBase
from BFHTW.models.document_main import Document
from BFHTW.utils.nxml.base_parser import BaseNXMLParser


class PubMedNXMLParser(BaseNXMLParser):
    """
    Parser for PubMed Central-style NXML files.
    Implements metadata and content extraction for PMC articles.
    """

    def __init__(self, file_path, doc_id, source_db, source_file=None):
        super().__init__(file_path, doc_id, source_db, source_file)
        self.tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1")

    def get_external_id(self, metadata: Dict[str, Optional[str]]) -> str:
        return self.get_text(".//article-id[@pub-id-type='pmc']") or \
               self.get_text(".//article-id[@pub-id-type='doi']") or \
               self.doc_id

    def get_publication_date(self) -> Optional[str]:
        return self.get_text(".//pub-date/year")

    def extract_authors(self) -> Optional[List[str]]:
        authors = []
        for contrib in self.root.xpath(".//contrib[@contrib-type='author']"):
            surname = contrib.findtext(".//surname")
            given_names = contrib.findtext(".//given-names")
            if surname and given_names:
                authors.append(f"{given_names} {surname}")
            elif surname:
                authors.append(surname)
        return authors or None

    def get_journal(self) -> Optional[str]:
        return self.get_text(".//journal-title")

    def get_doi(self) -> Optional[str]:
        return self.get_text(".//article-id[@pub-id-type='doi']")

    def get_clinical_trial_ref(self) -> Optional[str]:
        for el in self.root.xpath(".//ext-link[@ext-link-type='clinical-trial']"):
            if "NCT" in (text := "".join(el.itertext())):
                return text.strip()
        return None

    def extract_blocks(self) -> Generator[BlockBase, None, None]:
        section_counter = 0
        char_pointer = 0

        for sec in self.root.xpath(".//body//sec"):
            section_counter += 1
            section_title_el = sec.find("title")
            section_title = section_title_el.text.strip() if section_title_el is not None else None

            for para in sec.findall("p"):
                text = "".join(para.itertext()).strip()
                if not text:
                    continue

                token_count = len(self.tokenizer.encode(text, add_special_tokens=False))
                char_start = char_pointer
                char_end = char_start + len(text)
                char_pointer = char_end + 1

                yield BlockBase(
                    block_id=str(uuid4()),
                    doc_id=self.doc_id,
                    text=text,
                    section_index=section_counter,
                    section_title=section_title,
                    source="nxml",
                    block_type="paragraph",
                    page_num=None,
                    char_start=char_start,
                    char_end=char_end,
                    token_count=token_count,
                    language="en",
                    parser_version="v1.0.0",
                    created_at=datetime.utcnow().isoformat(),
                    embedding_exists=False,
                    ner_processed=False,
                    source_db=self.source_db,
                    source_file=self.source_file,
                )

    def get_document_metadata(self) -> Document:
        return Document(
            doc_id=self.doc_id,
            source_db=self.source_db,
            external_id=self.get_external_id({}),
            format="nxml",
            title=self.get_text(".//article-title"),
            source_file=self.source_file,
            retrieved_at=None,
            processed=False,
            has_figures=self.has_figures(),
            qdrant_synced=False,
            notes=None,
            search_tags=None,
            retrival_context=None,
            ingest_pipeline=None,
            license_type=self.extract_license_type(),
            publication_date=self.get_publication_date(),
            authors=self.extract_authors(),
            journal=self.get_journal(),
            abstract=self.extract_abstract(),
            doi=self.get_doi(),
            clinical_trial_ref=self.get_clinical_trial_ref(),
        )
