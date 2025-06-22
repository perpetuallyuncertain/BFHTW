from typing import List, Optional, Annotated
from pydantic import BaseModel, Field
from uuid import uuid4


class Document(BaseModel):
    """
    Master metadata record representing a biomedical document ingested from external sources
    (e.g., PubMed, arXiv). Links to block/NER/embedding tables and facilitates audit, search,
    and provenance tracking.
    """

    doc_id: Annotated[
        str,
        Field(
            default_factory=lambda: str(uuid4()),
            description="Universal UUID assigned internally to the document"
        )
    ]

    source_db: Annotated[
        str,
        Field(description="Name of the source database, e.g. 'pubmed_pmc', 'arxiv'")
    ]

    external_id: Annotated[
        str,
        Field(description="External ID from the source DB, e.g. PMC ID, arXiv ID")
    ]

    format: Annotated[
        str,
        Field(description="Original file format, e.g. 'pdf', 'nxml'")
    ]

    title: Annotated[
        Optional[str],
        Field(description="Title of the paper or preprint")
    ]

    source_file: Annotated[
        Optional[str],
        Field(description="Name of the file downloaded, e.g. 'PMC12345.tar.gz'")
    ]

    retrieved_at: Annotated[
        Optional[str],
        Field(description="Timestamp when this document was downloaded (ISO 8601)")
    ]

    processed: Annotated[
        bool,
        Field(default=False, description="True if fully parsed and indexed")
    ]

    has_figures: Annotated[
        Optional[bool],
        Field(default=None, description="True if figures/images were detected")
    ]

    qdrant_synced: Annotated[
        Optional[bool],
        Field(default=False, description="True if embeddings were uploaded to Qdrant")
    ]

    notes: Annotated[
        Optional[str],
        Field(default=None, description="Optional freeform notes or QA flags")
    ]

    search_tags: Annotated[
        Optional[List[str]],
        Field(default=None, description="List of tags or search terms used to retrieve this document")
    ]

    retrival_context: Annotated[
        Optional[str],
        Field(default=None, description="Text or query context that led to its retrieval")
    ]

    ingest_pipeline: Annotated[
        Optional[str],
        Field(default=None, description="Pipeline version or name that processed this doc")
    ]

    license_type: Annotated[
        Optional[str],
        Field(default=None, description="License type or access rights")
    ]

    publication_date: Annotated[
        Optional[str],
        Field(default=None, description="Publication date (ISO 8601)")
    ]

    authors: Annotated[
        Optional[List[str]],
        Field(default=None, description="List of authors")
    ]

    journal: Annotated[
        Optional[str],
        Field(default=None, description="Journal or conference name")
    ]

    abstract: Annotated[
        Optional[str],
        Field(default=None, description="Text of the abstract if extracted")
    ]

    clinical_trial_ref: Annotated[
        Optional[str],
        Field(default=None, description="Referenced clinical trial ID (e.g., NCT01234567)")
    ]

    doi: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Digital Object Identifier (DOI) if available. "
                        "Used for deduplication, metadata merging, and external reference matching."
        )
    ]

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "adf7b3b2-8df6-4f1e-a9f9-4cc915471c88",
                "source_db": "pubmed_pmc",
                "external_id": "PMC1234567",
                "format": "pdf",
                "title": "Irinotecan response in refractory hepatoblastoma",
                "source_file": "PMC1234567.tar.gz",
                "retrieved_at": "2025-06-21T10:30:00Z",
                "processed": True,
                "has_figures": True,
                "qdrant_synced": True,
                "notes": "Contains unparseable table on page 4",
                "search_tags": ["irinotecan", "refractory", "hepatoblastoma"],
                "retrival_context": "Query: efficacy of irinotecan in liver cancers",
                "ingest_pipeline": "biobert_v2.3_pdf_parser",
                "license_type": "CC-BY-NC",
                "publication_date": "2021-10-15",
                "authors": ["Doe J", "Smith A", "Tanaka K"],
                "journal": "Journal of Pediatric Oncology",
                "abstract": "This study investigates...",
                "clinical_trial_ref": "NCT04214418",
                "doi": "10.1038/s41586-024-04567-w"
            }
        }
