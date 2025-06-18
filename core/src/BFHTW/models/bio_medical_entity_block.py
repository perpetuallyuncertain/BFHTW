from typing import List, Optional, Annotated
from pydantic import BaseModel, Field, field_serializer

#-------------------------------------------------------------------------------
## Bio Filters

class BiomedicalEntityBlock(BaseModel):
    '''
    Structured model for biological entity filters extracted from a PDF block.
    Used for faceted search and cross-referencing block-level metadata.
    '''

    # Unique ID for the text block (e.g., paragraph or sentence) this data came from
    block_id: Annotated[str, Field(description="ID of the PDF block")]

    # ID of the full document this block belongs to
    doc_id: Annotated[str, Field(description="ID of the source document")]

    # Model tag for analysis later
    model: Annotated[str, Field(description="ID of the model used to create the keywords")]

    # Embeddings tag
    embeddings: Annotated[
        bool, 
        Field(
            default=False,
            description="Boolean to indicate if embeddings have been generated and saved to Qdrant"
            )
            ]

    # Drug and medication names (e.g., 'cisplatin', 'doxorubicin')
    medications: Optional[List[str]] = Field(default_factory=list)

    # Disease or disorder mentions (e.g., 'hepatoblastoma', 'HCC')
    diseases: Optional[List[str]] = Field(default_factory=list)

    # Clinical symptoms or signs (e.g., 'fever', 'abdominal pain')
    symptoms: Optional[List[str]] = Field(default_factory=list)

    # Therapeutic procedures mentioned (e.g., 'liver transplant', 'surgery')
    therapeutic_procedures: Optional[List[str]] = Field(default_factory=list)

    # Diagnostic procedures (e.g., 'MRI', 'biopsy', 'IHC staining')
    diagnostic_procedures: Optional[List[str]] = Field(default_factory=list)

    # Named clinical events (e.g., 'relapse', 'response', 'progression')
    clinical_events: Optional[List[str]] = Field(default_factory=list)

    # Biological structures mentioned (e.g., 'liver', 'tumor', 'cell membrane')
    biological_structures: Optional[List[str]] = Field(default_factory=list)

    # Quantitative or qualitative lab test values (e.g., 'elevated AFP')
    lab_values: Optional[List[str]] = Field(default_factory=list)

    # Any mention of dosage values (e.g., '50mg', '10 IU')
    dosages: Optional[List[str]] = Field(default_factory=list)

    # Temporal durations (e.g., '6 months', '2-week interval')
    durations: Optional[List[str]] = Field(default_factory=list)

    # Explicit time references (e.g., 'day 14', 'postoperative week 3')
    times: Optional[List[str]] = Field(default_factory=list)

    # Fallback bucket for unmatched or uncategorized entities
    other: Optional[List[str]] = Field(default_factory=list)

    @field_serializer("embeddings")
    def serialize_embeddings(self, val: bool) -> int:
        return int(val)