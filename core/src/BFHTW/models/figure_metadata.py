from typing import Optional, Annotated
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

class FigureMetadata(BaseModel):
    """
    Metadata for figures extracted from biomedical documents.
    
    Supports hybrid storage strategy with remote references and optional local caching
    for optimal performance and storage efficiency.
    """
    
    fig_id: Annotated[
        str,
        Field(
            default_factory=lambda: str(uuid4()),
            description="Unique figure ID (PK)"
        )
    ]
    
    doc_id: Annotated[
        str,
        Field(description="Document ID (FK) - references documents.doc_id")
    ]
    
    caption: Annotated[
        Optional[str],
        Field(default=None, description="Figure caption text")
    ]
    
    label: Annotated[
        Optional[str],
        Field(default=None, description="Figure label (e.g., 'Figure 1', 'Fig 2A')")
    ]
    
    # Remote reference fields (always available)
    external_url: Annotated[
        Optional[str],
        Field(default=None, description="Direct URL to figure on external source (PubMed, PMC, etc.)")
    ]
    
    archive_path: Annotated[
        Optional[str],
        Field(default=None, description="Path within downloaded archive/tar file")
    ]
    
    # Local cache fields (populated on-demand)
    local_path: Annotated[
        Optional[str],
        Field(default=None, description="Local cached file path (if downloaded)")
    ]
    
    cached_at: Annotated[
        Optional[datetime],
        Field(default=None, description="Timestamp when figure was cached locally")
    ]
    
    # Figure metadata
    page: Annotated[
        Optional[int],
        Field(default=None, description="Page number where figure appears")
    ]
    
    file_format: Annotated[
        Optional[str],
        Field(default=None, description="Image format (png, jpg, jpeg, svg, tiff, etc.)")
    ]
    
    file_size_bytes: Annotated[
        Optional[int],
        Field(default=None, description="File size in bytes")
    ]
    
    # Processing metadata
    extraction_method: Annotated[
        Optional[str],
        Field(default=None, description="Method used to extract figure (e.g., 'pdf_parsing', 'nxml_parsing')")
    ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "fig_id": "fig_123e4567-e89b-12d3-a456-426614174000",
                "doc_id": "doc_987fcdeb-51a2-43d7-8f6e-123456789abc",
                "caption": "Kaplan-Meier survival curves for hepatoblastoma patients by treatment group.",
                "label": "Figure 2A",
                "external_url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/bin/fig2.jpg",
                "archive_path": "PMC1234567/figures/fig2.jpg",
                "local_path": None,
                "cached_at": None,
                "page": 5,
                "file_format": "jpg",
                "file_size_bytes": 156789,
                "extraction_method": "nxml_parsing"
            }
        }
