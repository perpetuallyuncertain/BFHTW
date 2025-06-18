# utils/pdf/pdf_block_extractor.py
import fitz
import uuid
import json
from pathlib import Path
from typing import List, NamedTuple, Optional
from datetime import datetime
from BFHTW.utils.logs import get_logger
from BFHTW.models.pdf_extraction import PDFMetadata, PDFBlock

L = get_logger()

class PDFExtractionResult(NamedTuple):
    metadata: Optional[PDFMetadata]
    blocks: List[PDFBlock]

class PDFBlockExtractor:
    """Generic class to extract structured block data from a PDF."""

    @staticmethod
    def extract_blocks(doc, doc_id: str) -> List[PDFBlock]:
        all_blocks = []

        for page_num, page in enumerate(doc):
            for block_index, block in enumerate(page.get_text("dict")["blocks"]):
                lines = block.get("lines", [])
                text_lines = []
                font_size = font_name = color = None

                for line in lines:
                    for span in line.get("spans", []):
                        if span["text"].strip():
                            text_lines.append(span["text"])
                            font_size = font_size or span.get("size")
                            font_name = font_name or span.get("font")
                            color = color or span.get("color")

                text = " ".join(text_lines).strip()
                if not text:
                    continue

                all_blocks.append(PDFBlock(
                    block_id=str(uuid.uuid4()),
                    doc_id=doc_id,
                    page=page_num,
                    block_index=block_index,
                    text=text,
                    bbox=json.dumps(block["bbox"]),
                    font_size=font_size,
                    font_name=font_name,
                    color=color,
                    line_count=len(lines),
                    tokens=len(text.split()),
                    created_at=datetime.now().isoformat(),
                    processed=False
                ))

        return all_blocks

    @classmethod
    def read_pdf(cls, pdf_path: Path, doc_id: Optional[str] = None) -> PDFExtractionResult:
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        doc = fitz.open(pdf_path)
        L.info(f"Opened PDF: {pdf_path}")

        meta_raw = doc.metadata or {}
        metadata = PDFMetadata(
            doc_id=doc_id,
            title=meta_raw.get("title"),
            author=meta_raw.get("author"),
            subject=meta_raw.get("subject"),
            keywords=meta_raw.get("keywords"),
            creator=meta_raw.get("creator"),
            producer=meta_raw.get("producer"),
            creationDate=meta_raw.get("creationDate"),
            modDate=meta_raw.get("modDate"),
            trapped=meta_raw.get("trapped"),
            encryption=meta_raw.get("encryption"),
            format=meta_raw.get("format"),
            file_path=str(pdf_path),
        )

        blocks = cls.extract_blocks(doc, doc_id)
        return PDFExtractionResult(metadata=metadata, blocks=blocks)
