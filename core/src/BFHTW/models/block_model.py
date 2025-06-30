from typing import Optional, Annotated
from pydantic import BaseModel, Field
from uuid import uuid4

#-------------------------------------------------------------------------------
# BlockData

class BlockBase(BaseModel):
    """
    Base model for all document text blocks (PDF, NXML, etc).
    Includes standard text, location, and processing status fields.
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
        Field(default=None, description="Section index if available")
    ]
    section_title: Annotated[
        Optional[str],
        Field(default=None, description="Section title if available")
    ]
    source: Annotated[
        Optional[str],
        Field(default=None, description="Source file format, e.g., 'pdf', 'nxml'")
    ]
    block_type: Annotated[
        Optional[str],
        Field(default=None, description="Block role: 'paragraph', 'caption', etc.")
    ]
    page_num: Annotated[
        Optional[int],
        Field(default=None, description="Page number (if known or estimated)")
    ]
    char_start: Annotated[
        Optional[int],
        Field(default=None, description="Start character offset in the document")
    ]
    char_end: Annotated[
        Optional[int],
        Field(default=None, description="End character offset in the document")
    ]
    language: Annotated[
        Optional[str],
        Field(default=None, description="Language of the block")
    ]
    parser_version: Annotated[
        Optional[str],
        Field(default=None, description="Version of the parser used to extract block")
    ]
    created_at: Annotated[
        Optional[str],
        Field(default=None, description="ISO timestamp of block creation")
    ]
    embedding_exists: Annotated[
        bool,
        Field(default=False, description="True if embeddings were generated")
    ]
    ner_processed: Annotated[
        bool,
        Field(default=False, description="True if NER was completed")
    ]

    token_count: Annotated[
        Optional[int],
        Field(default=None, description="Number of tokens in the block text")
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
                "page_num": 5,
                "char_start": 4567,
                "char_end": 4688,
                "language": "en",
                "parser_version": "v1.2.0",
                "created_at": "2023-10-01T12:00:00+00:00",
                "embedding_exists": False,
                "ner_processed": False
            }
        }
