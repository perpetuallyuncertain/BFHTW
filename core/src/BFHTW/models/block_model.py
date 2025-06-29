from typing import Optional, Annotated
from pydantic import BaseModel, Field
from uuid import uuid4

#-------------------------------------------------------------------------------
# BlockData

from typing import Optional, Annotated
from pydantic import BaseModel, Field
from uuid import uuid4

class BlockBase(BaseModel):
    """
    Base model for all document text blocks (PDF, NXML, etc).
    Only includes fields common to all formats.
    """
    block_id: Annotated[
        str,
        Field(default_factory=lambda: str(uuid4()), description="Unique block ID")
    ]

    doc_id: Annotated[
        str,
        Field(description="ID of the source document")
    ]

    text: Annotated[
        str,
        Field(description="Raw text content")
    ]

    section_index: Annotated[
        Optional[int],
        Field(default=None, description="Section index if available (e.g., NXML or derived from headings)")
    ]

    section_title: Annotated[
        Optional[str],
        Field(default=None, description="Section title if available")
    ]

    source: Annotated[
        Optional[str],
        Field(default=None, description="File type source, e.g., 'pdf', 'nxml'")
    ]

    block_type: Annotated[
        Optional[str],
        Field(default=None, description="Block role: 'paragraph', 'caption', 'abstract', etc.")
    ]

    parser_version: Annotated[
        Optional[str],
        Field(default=None, description="Version of the parser used")
    ]

    language: Annotated[
        Optional[str],
        Field(default=None, description="Language detected in the block")
    ]

    created_at: Annotated[
        Optional[str],
        Field(default=None, description="ISO timestamp of block creation")
    ]

    embedding_exists: Annotated[
        bool,
        Field(default=False, description="Whether embeddings exist for this block")
    ]

    ner_processed: Annotated[
        bool,
        Field(default=False, description="Whether NER was completed for this block")
    ]

class Config:
    json_schema_extra = {
        "example": {
            "block_id": "1d5e87e6-3abf-4c67-b4f5-7988f1b68bcf",
            "doc_id": "PMC1234567",
            "text": "Integrated analysis of somatic mutations and focal copy-number changes",
            "section_index": 3,
            "section_title": "Results",
            "source": "pdf",
            "block_type": "paragraph",
            "language": "en",
            "parser_version": "v1.2.0",
            "created_at": "2023-10-01T12:00:00+00:00",
            "embedding_exists": False,
            "ner_processed": False
        }
    }


#-------------------------------------------------------------------------------
# Metadata

class PDFMetadata(BaseModel):
    '''
    Model representing metadata extracted from a PDF file.
    '''

    doc_id: Annotated[
        str, 
        Field(default_factory=lambda: str(uuid4()), description="Unique document ID")]

    format: Annotated[
        Optional[str],
        Field(description="The PDF version and format")
    ]

    title: Annotated[
        Optional[str],
        Field(default=None, description="Title of the PDF document")
    ]

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

    file_path: Annotated[
        str,
        Field(default=None, description="Path to the PDF file on disk")
    ]

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "123e4567-e89b-12d3-a456-426614174000",
                "format": "PDF 1.7",
                "title": "The genomic landscape of hepatoblastoma and their progenies with HCC-like features",
                "author": "Melanie Eichenmüller",
                "subject": "Journal of Hepatology, 61 (2014) 1312-1320. doi:10.1016/j.jhep.2014.08.009",
                "keywords": "",
                "creator": "Elsevier",
                "producer": "Acrobat Distiller 8.0.0 (Windows)",
                "creationDate": "D:20141021194648+05'30'",
                "modDate": "D:20150928152500+05'30'",
                "trapped": "",
                "encryption": None,
                "file_path": "/path/to/document.pdf"
            }
        }