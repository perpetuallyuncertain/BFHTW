# pubmed_parser.py
from typing import Dict, Generator
import uuid
from BFHTW.utils.nxml.base_parser import BaseNXMLParser
from BFHTW.models.bio_medical_entity_block import BiomedicalEntityBlock

class PubMedNXMLParser(BaseNXMLParser):
    def extract_blocks(self) -> Generator[BiomedicalEntityBlock]:
        section_counter = 0
        for sec in self.root.xpath(".//body//sec"):
            section_counter += 1
            title_el = sec.find("title")
            section_title = title_el.text.strip() if title_el is not None else None
            for para in sec.findall("p"):
                yield {
                    "block_id": 
                    "section_index": section_counter,
                    "section_title": section_title,
                    "text": "".join(para.itertext()).strip()
                }
