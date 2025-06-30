from typing import Optional, Annotated
from pydantic import BaseModel, Field
from uuid import uuid4

#-------------------------------------------------------------------------------
# PDF Block to be used to supplement the block base for PDF file parsing.
from BFHTW.models.block_model import BlockBase

class PDFBlock(BlockBase):
    """
    Extended block model for PDF-specific attributes.

    Includes layout, font, and geometry metadata extracted from the PDF file
    in addition to standard semantic and structural fields from BlockBase.
    """

    page: Annotated[
        Optional[int],
        Field(default=None, description="Page number the block is on")
    ]

    block_index: Annotated[
        Optional[int],
        Field(default=None, description="Index of the block within the page")
    ]

    bbox: Annotated[
        Optional[str],
        Field(default=None, description="Serialized bounding box as JSON string (x0, y0, x1, y1)")
    ]

    font_size: Annotated[
        Optional[float],
        Field(default=None, description="Font size of the block text")
    ]

    font_name: Annotated[
        Optional[str],
        Field(default=None, description="Font name used in the block")
    ]

    color: Annotated[
        Optional[int],
        Field(default=None, description="Color code of the font")
    ]

    line_count: Annotated[
        Optional[int],
        Field(default=None, description="Number of lines in the block")
    ]

    tokens: Annotated[
        Optional[int],
        Field(default=None, description="Token count for embedding preparation")
    ]

    class Config(BlockBase.Config):
        json_schema_extra = {
            "example": {
                "block_id": "1d5e87e6-3abf-4c67-b4f5-7988f1b68bcf",
                "doc_id": "PMC1234567",
                "text": "Integrated analysis of somatic mutations and focal copy-number changes",
                "section_index": 2,
                "section_title": "Genomic Alterations",
                "source": "pdf",
                "block_type": "paragraph",
                "language": "en",
                "parser_version": "v1.2.0",
                "created_at": "2023-10-01T12:00:00+00:00",
                "embedding_exists": False,
                "ner_processed": False,
                "page": 3,
                "block_index": 7,
                "bbox": "[74.4, 86.4, 298.2, 92.8]",
                "font_size": 6.38,
                "font_name": "AdvGulliv-R",
                "color": 32941,
                "line_count": 2,
                "tokens": 18
            }
        }

#-------------------------------------------------------------------------------
from BFHTW.models.meta_model import MetaBase

class PDFMetadata(MetaBase):
    """
    Extended metadata model with PDF-specific fields, inheriting shared fields from MetadataBase.
    """

    author: Annotated[
        Optional[str],
        Field(default=None, description="Author of the PDF document")
    ]

    subject: Annotated[
        Optional[str],
        Field(default=None, description="Subject or abstract of the document")
    ]

    keywords: Annotated[
        Optional[str],
        Field(default=None, description="Comma-separated list of keywords")
    ]

    creator: Annotated[
        Optional[str],
        Field(default=None, description="Original application used to create the PDF")
    ]

    producer: Annotated[
        Optional[str],
        Field(default=None, description="PDF producer software")
    ]

    creation_date: Annotated[
        Optional[str],
        Field(default=None, description="Original creation date in PDF datetime format (e.g., D:YYYYMMDDHHMMSS+TZ)")
    ]

    modification_date: Annotated[
        Optional[str],
        Field(default=None, description="Last modified date in PDF datetime format")
    ]

    trapped: Annotated[
        Optional[str],
        Field(default=None, description="Trapping status of the PDF (usually '', 'True', or 'False')")
    ]

    encryption: Annotated[
        Optional[str],
        Field(default=None, description="Encryption status if any (None if not encrypted)")
    ]

    class Config(MetaBase.Config):
        json_schema_extra = {
            "example": {
                "doc_id": "123e4567-e89b-12d3-a456-426614174000",
                "format": "PDF 1.7",
                "title": "The genomic landscape of hepatoblastoma and their progenies with HCC-like features",
                "file_path": "/path/to/document.pdf",
                "author": "Melanie Eichenmüller",
                "subject": "Journal of Hepatology, 61 (2014) 1312-1320. doi:10.1016/j.jhep.2014.08.009",
                "keywords": "",
                "creator": "Elsevier",
                "producer": "Acrobat Distiller 8.0.0 (Windows)",
                "creation_date": "D:20141021194648+05'30'",
                "modification_date": "D:20150928152500+05'30'",
                "trapped": "",
                "encryption": None
            }
        }
