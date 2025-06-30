# base_parser.py
from abc import ABC, abstractmethod
from pathlib import Path
from lxml import etree
from typing import Dict, Generator, Optional, List
from BFHTW.models.meta_model import MetaBase
from BFHTW.models.block_model import BlockBase


class BaseNXMLParser(ABC):
    """
    Abstract base parser for NXML-like documents.
    Defines a standard interface and core utilities required to populate a Document record.
    Subclasses must implement extraction logic for source-specific fields.
    """

    def __init__(self, file_path: str, doc_id: str, source_db: str, source_file: Optional[str] = None):
        self.file_path = Path(file_path)
        self.tree = etree.parse(str(self.file_path), parser=None)
        self.root = self.tree.getroot()
        self.doc_id = doc_id
        self.source_db = source_db
        self.source_file = source_file

    # -------------------------------------------------------------------------
    # Required metadata extraction (must be implemented by subclasses)
    # -------------------------------------------------------------------------

    @abstractmethod
    def get_external_id(self, metadata: Dict[str, Optional[str]]) -> str:
        """Returns the canonical external identifier (PMC ID, DOI, etc)."""
        pass

    @abstractmethod
    def get_publication_date(self) -> Optional[str]:
        """Returns ISO-8601 publication date if available."""
        pass

    @abstractmethod
    def extract_authors(self) -> Optional[List[str]]:
        """Returns a list of author names in display-ready format."""
        pass

    # -------------------------------------------------------------------------
    # Metadata object construction (unified output for SQL model)
    # -------------------------------------------------------------------------

    def save_metadata(self, metadata: Dict[str, Optional[str]]) -> MetaBase:
        return MetaBase(
            doc_id=self.doc_id,
            title=metadata.get("title"),
            format="nxml",
            file_path=str(self.file_path)
        )

    # -------------------------------------------------------------------------
    # Optional utilities (available to all subclasses)
    # -------------------------------------------------------------------------

    def extract_license_type(self) -> Optional[str]:
        for action, pi in etree.iterwalk(self.tree, events=("PI",)):
            if pi.target == "properties" and "open_access" in pi.text:
                return "open_access"
        return None

    def has_figures(self) -> bool:
        return bool(self.root.xpath(".//fig"))

    def extract_abstract(self) -> Optional[str]:
        abstract_el = self.root.find(".//abstract")
        if abstract_el is not None:
            return "\n\n".join(
                ["".join(p.itertext()).strip() for p in abstract_el.findall(".//p")]
            ) or None
        return None

    def get_text(self, xpath: str) -> Optional[str]:
        el = self.root.xpath(xpath)
        return el[0].text.strip() if el and el[0].text else None

    def save_block(self, block: BlockBase):
        print(f"[DEBUG] Saving block: {block.model_dump()}")

    def get_metadata(self) -> Dict[str, Optional[str]]:
        return {
            "title": self.get_text(".//article-title"),
            "format": "nxml",
            "file_path": str(self.file_path)
        }

    # -------------------------------------------------------------------------
    # Must be implemented: yields structured block objects from the file
    # -------------------------------------------------------------------------

    @abstractmethod
    def extract_blocks(self) -> Generator[BlockBase, None, None]:
        """
        Extracts all semantic content blocks from the NXML tree and yields
        them one at a time, formatted as `BlockBase`-compatible models or dicts.
        """
        pass
