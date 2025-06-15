from typing import List, Optional, Tuple, Annotated
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime

#-------------------------------------------------------------------------------
# BlockData

class BlockData(BaseModel):
    '''
    Represents a block of text extracted from a document.

    Captures essential attributes such as position, content, metadata, semantic annotations,
    and embedding information for use in downstream indexing or analysis.
    '''

    block_id: Annotated[
        str,
        Field(
            default_factory=lambda: str(uuid4()),
            description="Unique ID for the block"
        )
    ]

    doc_id: Annotated[
        str,
        Field(
            description="Reference to the parent document ID"
        )
    ]

    page: Annotated[
        int,
        Field(
            description="Page number the block is on"
        )
    ]

    block_index: Annotated[
        int,
        Field(
            description="Index of the block within the page"
        )
    ]

    text: Annotated[
        str,
        Field(
            description="Raw text content of the block"
        )
    ]
    bbox: Annotated[
        str,
        Field(
            description="Serialized bounding box as a JSON string representing (x0, y0, x1, y1)"
        )
    ]

    font_size: Annotated[
        Optional[float],
        Field(
            default=None,
            description="Font size of the block text"
        )
    ]

    font_name: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Font name used in the block"
        )
    ]

    color: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Color code of the font"
        )
    ]

    line_count: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Number of lines in the block"
        )
    ]

    tokens: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Token count for embedding preparation"
        )
    ]

    created_at: Annotated[
        Optional[str],
        Field(description="Timestamp when the block was created, in ISO format")
    ]

    processed: Annotated[
        bool,
        Field(
            default=False,
            description="Flag indicating if the block has been processed for indexing"
        )
    ]

    class Config:
        json_schema_extra = {
            "example": {
                "block_id": "1d5e87e6-3abf-4c67-b4f5-7988f1b68bcf",
                "doc_id": "PMC1234567",
                "page": 3,
                "block_index": 7,
                "text": "Integrated analysis of somatic mutations and focal copy-number changes",
                "bbox": [74.4, 86.4, 298.2, 92.8],
                "font_size": 6.38,
                "font_name": "AdvGulliv-R",
                "color": 32941,
                "line_count": 2,
                "tokens": 18,
                "created_at": "2023-10-01T12:00:00+00:00",
                "processed": False
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
        str,
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

    creationDate: Annotated[
        Optional[str],
        Field(default=None, description="Original creation date in PDF datetime format (e.g., D:YYYYMMDDHHMMSS+TZ)")
    ]

    modDate: Annotated[
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

#-------------------------------------------------------------------------------
## Bio Filters

class FilterModel(BaseModel):
    '''
    Structured model for biological entity filters extracted from a PDF block.
    Used for faceted search and cross-referencing block-level metadata.
    '''

    block_id: Annotated[
        str,
        Field(description="Unique ID for the associated text block, matching the block table.")
    ]

    doc_id: Annotated[
        str,
        Field(description="Document ID that this block belongs to, matching the metadata table.")
    ]

    genes: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Gene names detected (e.g., TP53, CTNNB1).")
    ]

    proteins: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Proteins mentioned (e.g., beta-catenin, p53).")
    ]

    mutations: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Mutation identifiers (e.g., V600E, exon 3 del).")
    ]

    pathways: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Biological pathways (e.g., Wnt, Notch, PI3K/Akt).")
    ]

    drugs: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Drugs or chemotherapies (e.g., cisplatin, doxorubicin).")
    ]

    diseases: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Diseases referenced (e.g., hepatoblastoma, HCC).")
    ]

    tissues: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Tissue types (e.g., liver, lung, tumor sample).")
    ]

    biomarkers: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Known biomarkers (e.g., AFP, glypican-3).")
    ]

    treatments: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Therapeutic approaches (e.g., surgery, chemo, transplant).")
    ]

    clinical_phase: Annotated[
        Optional[str],
        Field(default=None, description="Clinical stage if stated (e.g., 'Phase II', 'preclinical').")
    ]

    sample_type: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Experimental sample type (e.g., cell line, patient tissue, xenograft).")
    ]

    methods: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="Research methods (e.g., RNA-seq, IHC, Western blot).")
    ]