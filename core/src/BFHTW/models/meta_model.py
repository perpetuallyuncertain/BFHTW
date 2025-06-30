from typing import Optional, Annotated
from pydantic import BaseModel, Field
from uuid import uuid4

class MetaBase(BaseModel):
    """
    Base metadata model common to all document types (PDF, NXML, etc.).
    """

    doc_id: Annotated[
        str,
        Field(default_factory=lambda: str(uuid4()), description="Unique internal document ID")
    ]

    title: Annotated[
        Optional[str],
        Field(default=None, description="Title of the document")
    ]

    format: Annotated[
        Optional[str],
        Field(default=None, description="Format of the document (e.g., 'pdf', 'nxml')")
    ]

    file_path: Annotated[
        Optional[str],
        Field(default=None, description="Filesystem path to the document")
    ]

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "The genomic landscape of hepatoblastoma",
                "format": "nxml",
                "file_path": "/data/pmc/articles/PMC1234567.nxml"
            }
        }