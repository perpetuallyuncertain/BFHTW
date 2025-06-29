"""
PDF Block Extraction Module

Responsible for:
- Parsing a PDF (fitz.Document)
- Extracting structured blocks of text with metadata
"""

import fitz
import uuid
import json
from pathlib import Path
from typing import List
from datetime import datetime

from BFHTW.utils.logs import get_logger
from BFHTW.models.pdf_models import PDFBlock

L = get_logger()


class PDFBlockExtractor:
    """Extracts text blocks from a fitz.Document and converts them to PDFBlock objects."""

    @staticmethod
    def extract_blocks(pdf_path: Path, doc_id: str) -> List[PDFBlock]:
        all_blocks: List[PDFBlock] = []

        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            try:
                block_items = page.get_text("dict")["blocks"] # type: ignore
            except Exception as e:
                L.warning(f"Failed to extract blocks from page {page_num}: {e}")
                continue

            for block_index, block in enumerate(block_items):
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
                    bbox=json.dumps(block.get("bbox", [])),
                    font_size=font_size,
                    font_name=font_name,
                    color=color,
                    line_count=len(lines),
                    tokens=len(text.split()),
                    created_at=datetime.now().isoformat(),
                    processed=False
                ))

        L.info(f"Extracted {len(all_blocks)} blocks from PDF {doc_id}")
        return all_blocks
