"""
PDF Reader Module

Responsible for:
- Opening PDF files using PyMuPDF
- Extracting high-level metadata for storage or analysis
"""

import fitz
import uuid
from pathlib import Path
from typing import Optional

from BFHTW.models.pdf_extraction import PDFMetadata
from BFHTW.utils.logs import get_logger

L = get_logger()


class PDFReadMeta:
    """Reads and extracts only metadata from a PDF file."""

    @classmethod
    def extract_metadata(cls, pdf_path: Path, doc_id: Optional[str] = None) -> Optional[PDFMetadata]:
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            L.error(f"Failed to open PDF file: {pdf_path} — {e}")
            return None

        raw_meta = doc.metadata or {}
        if not raw_meta:
            L.warning(f"No metadata found in PDF: {pdf_path}")
        
        metadata = PDFMetadata(
            doc_id=doc_id,
            title=raw_meta.get("title"),
            author=raw_meta.get("author"),
            subject=raw_meta.get("subject"),
            keywords=raw_meta.get("keywords"),
            creator=raw_meta.get("creator"),
            producer=raw_meta.get("producer"),
            creation_date=raw_meta.get("creationDate"),
            modification_date=raw_meta.get("modDate"),
            trapped=raw_meta.get("trapped"),
            encryption=raw_meta.get("encryption"),
            format=raw_meta.get("format"),
            file_path=str(pdf_path)
        )

        L.info(f"Extracted metadata from PDF: {pdf_path}")
        return metadata
