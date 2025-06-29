# base_parser.py
from abc import ABC, abstractmethod
from pathlib import Path
from lxml import etree
from typing import Dict, Generator, Optional, List
from BFHTW.models.document_main import Document
from BFHTW.models.bio_medical_entity_block import BiomedicalEntityBlock


class BaseNXMLParser(ABC):
    def __init__(self, file_path: str, doc_id: str, source_db: str, source_file: Optional[str] = None):
        self.file_path = Path(file_path)
        self.tree = etree.parse(str(self.file_path), parser=None)
        self.root = self.tree.getroot()
        self.source_db = source_db
        self.source_file = source_file
        self.doc_id = doc_id

    def save_metadata(self, metadata: Dict[str, Optional[str]]) -> Document:
        doc = Document(
            source_db=self.source_db,
            external_id=self.get_external_id(metadata),
            format="nxml",
            title=metadata.get("title"),
            source_file=self.source_file,
            publication_date=metadata.get("pub_date"),
            journal=metadata.get("journal"),
            doi=metadata.get("doi"),
            license_type=self.extract_license_type(),
            processed=True,
            doc_id=self.doc_id,
            retrieved_at=None,
            has_figures=self.has_figures(),
            qdrant_synced=False,
            notes=None,
            search_tags=None,
            retrival_context=None,
            ingest_pipeline=None,
            authors=self.extract_authors(),
            abstract=self.extract_abstract(),
            clinical_trial_ref=None
        )
        print(f"[DEBUG] Document created: {doc.model_dump()}")
        return doc

    def get_external_id(self, metadata: Dict[str, Optional[str]]) -> str:
        """Allow subclasses to override how external_id is resolved"""
        return metadata.get("pmcid") or metadata.get("doi") or "unknown"

    def save_block(self, block: Dict[str, str]):
        print(f"[DEBUG] Saving block: {block}")
        # In real implementation: embed + push to vector store

    def get_metadata(self) -> Dict[str, Optional[str]]:
        return {
            "pmcid": self.get_text(".//article-id[@pub-id-type='pmc']"),
            "doi": self.get_text(".//article-id[@pub-id-type='doi']"),
            "title": self.get_text(".//article-title"),
            "journal": self.get_text(".//journal-title"),
            "pub_date": self.get_text(".//pub-date/year"),
        }

    def extract_license_type(self) -> Optional[str]:
        for action, pi in etree.iterwalk(self.tree, events=("PI",)):
            if pi.target == "properties" and "open_access" in pi.text:
                return "open_access"
        return None

    def has_figures(self) -> bool:
        return bool(self.root.xpath(".//fig"))

    def extract_authors(self) -> Optional[List[str]]:
        authors = []
        for name_el in self.root.xpath(".//contrib-group/contrib[@contrib-type='author']/name"):
            given = name_el.findtext("given-names") or ""
            surname = name_el.findtext("surname") or ""
            full_name = f"{surname} {given}".strip()
            if full_name:
                authors.append(full_name)
        return authors or None

    def extract_abstract(self) -> Optional[str]:
        abstract_el = self.root.find(".//abstract")
        if abstract_el is not None:
            return "\n\n".join(
                ["".join(p.itertext()).strip() for p in abstract_el.findall(".//p")]
            ) or None
        return None

    def get_text(self, xpath: str) -> Optional[str]:
        el = self.root.xpath(xpath)
        return el[0].text.strip() if el else None

    @abstractmethod
    def extract_blocks(self) -> Generator[BiomedicalEntityBlock]:
        pass
