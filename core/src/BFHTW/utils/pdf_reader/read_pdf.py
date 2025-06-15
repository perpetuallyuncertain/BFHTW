'''
Extracts blocks of text from a PDF file using PyMuPDF (fitz).  Returns the block data as a list of BlockData objects.

'''

import fitz
import uuid
import json

from pathlib import Path
from typing import Generic, List, TypeVar, NamedTuple
from pydantic import BaseModel
from datetime import datetime

from BFHTW.utils.logs import get_logger
from BFHTW.models.articles.pydantic import BlockData, PDFMetadata

L = get_logger()
#-------------------------------------------------------------------------------

# Declare a TypeVar for any ResponseModel that's a subclass of BaseModel
# Then we can support typing but allow the schema to be provided at runtime

AnyResponseModel = TypeVar('AnyResponseModel', bound=BaseModel)

class PDFExtractionResult(NamedTuple):
    metadata: PDFMetadata
    blocks: List[BlockData]

class ReadPDF(Generic[AnyResponseModel]):
    '''Base class for reading PDF files and extracting structured data.'''
    
    base_dir = Path(__file__).parent.parent.parent

    @classmethod
    def extract_blocks_from_pdf(cls, doc: object, doc_id: str) -> List[BlockData]:
        all_blocks = []

        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block_index, block in enumerate(blocks):
                lines = block.get("lines", [])
                text_lines = []
                font_size = None
                font_name = None
                color = None

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

                block_data = BlockData(
                    block_id=str(uuid.uuid4()),  # Generate a unique block ID
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
                    created_at=str(datetime.now(tz=None).isoformat()),
                    processed=False
                )

                all_blocks.append(block_data)

        return all_blocks

    @classmethod
    def get_pdf_data(cls, pdf_filename: str, doc_id: str = None) -> PDFExtractionResult:
        '''Extract metadata and block data from a PDF file.'''
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        pdf_path = cls.base_dir / pdf_filename
        doc = fitz.open(pdf_path)

        if not doc:
            L.error(f"Failed to open PDF file: {pdf_filename}")
            return PDFExtractionResult(metadata=None, blocks=[])

        L.info(f"Opened PDF file: {pdf_filename}")

        meta_raw = doc.metadata
        if not meta_raw:
            L.warning(f"No metadata found in PDF file: {pdf_filename}")
            return PDFExtractionResult(metadata=None, blocks=[])

        metadata = PDFMetadata(
            doc_id=doc_id,
            title=meta_raw.get("title"),
            author=meta_raw.get("author"),
            subject=meta_raw.get("subject"),
            keywords=meta_raw.get("keywords"),
            creator=meta_raw.get("creator"),
            producer=meta_raw.get("producer"),
            creation_date=meta_raw.get("creationDate"),
            modification_date=meta_raw.get("modDate"),
            format=meta_raw.get("format"),
            file_path=str(pdf_path)
        )

        blocks = cls.extract_blocks_from_pdf(doc, doc_id)
        return PDFExtractionResult(metadata=metadata, blocks=blocks)