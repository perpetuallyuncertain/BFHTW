# Data Models

Comprehensive Pydantic models for biomedical document processing and clinical data extraction. These models provide the foundation for BFHTW's structured approach to biomedical literature analysis, ensuring data consistency and enabling advanced search capabilities.

## Overview

The models module contains all data structures used throughout BFHTW, designed with the following principles:

- **Type Safety**: Full Pydantic validation with type hints
- **Database Alignment**: Direct mapping to database schema relationships
- **Extensibility**: Base classes for easy customization
- **Performance**: Optimized for high-volume document processing

## Core Model Categories

### Document Models
- **Document**: Master metadata record for all documents
- **MetaBase**: Common metadata fields across document types
- **PDFMetadata**: PDF-specific metadata and properties
- **NXMLMetadata**: NXML-specific metadata and structure

### Text Block Models
- **BlockBase**: Foundation for all text extraction
- **PDFBlock**: PDF-specific blocks with layout information
- **NXMLBlock**: NXML blocks with semantic structure
- **BiomedicalEntityBlock**: Blocks with extracted clinical entities

### Biomedical Entity Models
- **KeywordMention**: Precise entity locations within text
- **ClinicalMarker**: Gene expressions and biomarkers
- **TreatmentRegimen**: Therapy protocols and outcomes
- **ResistancePattern**: Drug resistance mechanisms

### Figure and Media Models
- **FigureMetadata**: Hybrid storage for document figures
- **ImageCache**: Local caching management
- **MediaReference**: External media resource links

### Search and Vector Models
- **QdrantEmbeddingModel**: Vector embeddings for semantic search
- **SearchResult**: Structured search response format
- **SimilarityScore**: Document similarity metrics

### Clinical Research Models
- **PMCArticleMetadata**: PubMed Central article information
- **ClinicalTrial**: Trial metadata and outcomes
- **PatientCohort**: Study population characteristics
- **TreatmentOutcome**: Efficacy and safety results

## Model Architecture

### Database Schema Alignment
All models directly correspond to the database schema shown in `biomed_schema.png`:

```sql
-- Primary entities with relationships
documents (doc_id PK)
├── blocks (block_id PK, doc_id FK)
├── keyword_mentions (block_id FK, doc_id FK)  
├── figure_metadata (fig_id PK, doc_id FK)
├── raw_pdf_metadata (doc_id FK)
├── raw_nxml_metadata (doc_id FK)
└── processing_log (doc_id FK)
```

### Inheritance Hierarchy
```python
# Base Models
BaseModel (Pydantic)
├── MetaBase
│   ├── PDFMetadata
│   └── NXMLMetadata
├── BlockBase
│   ├── PDFBlock
│   ├── NXMLBlock
│   └── BiomedicalEntityBlock
└── Document

# Specialized Models
QdrantEmbeddingModel
FigureMetadata
PMCArticleMetadata
```

## File Organization

```
models/
├── __init__.py                     # Package initialization
├── bio_medical_entity_block.py     # Clinical entity extraction
├── block_model.py                  # Base text block model
├── document_main.py                # Master document model
├── figure_metadata.py              # Figure storage with hybrid caching
├── meta_model.py                   # Base metadata model
├── nxml_models.py                  # NXML-specific models
├── pdf_models.py                   # PDF-specific models
├── pubmed_pmc.py                   # PMC article metadata
├── qdrant.py                       # Vector embedding models
└── README.md                       # This file
```

## Usage Examples

### Document Processing
```python
from BFHTW.models.document_main import Document
from BFHTW.models.pdf_models import PDFMetadata, PDFBlock

# Create document record
doc = Document(
    source_db="pubmed_pmc",
    external_id="PMC1234567",
    format="pdf",
    title="Hepatoblastoma Treatment Outcomes"
)

# Process PDF content
pdf_meta = PDFMetadata(doc_id=doc.doc_id, ...)
pdf_blocks = [PDFBlock(doc_id=doc.doc_id, ...) for block in extracted_blocks]
```

### Clinical Entity Extraction
```python
from BFHTW.models.bio_medical_entity_block import BiomedicalEntityBlock

# Store extracted clinical entities
entity_block = BiomedicalEntityBlock(
    block_id="block_123",
    doc_id="doc_456", 
    model="biobert_v1.0",
    medications=["cisplatin", "doxorubicin"],
    diseases=["hepatoblastoma", "liver_cancer"],
    symptoms=["abdominal_pain", "jaundice"],
    embeddings=True
)
```

### Figure Management
```python
from BFHTW.models.figure_metadata import FigureMetadata

# Hybrid figure storage
figure = FigureMetadata(
    doc_id="doc_123",
    caption="Kaplan-Meier survival curves",
    label="Figure 2A",
    external_url="https://pmc.ncbi.nlm.nih.gov/...",
    archive_path="PMC1234/figures/fig2.jpg",
    # local_path populated on-demand
)
```

### Vector Search
```python
from BFHTW.models.qdrant import QdrantEmbeddingModel

# Store semantic embeddings
embedding = QdrantEmbeddingModel(
    doc_id="doc_123",
    block_id="block_456", 
    embedding=[0.1, 0.2, ...],  # 768-dim BioBERT
    text="Treatment with cisplatin showed...",
    page=5
)
```

## Validation and Quality Assurance

### Built-in Validation
- **Field Types**: Strict type checking with Pydantic
- **Value Constraints**: Min/max lengths, regex patterns
- **Foreign Key Integrity**: Document ID consistency
- **Optional Fields**: Graceful handling of incomplete data

### Example Validation
```python
from pydantic import ValidationError

try:
    block = BiomedicalEntityBlock(
        block_id="invalid",  # Will validate UUID format
        doc_id="doc_123",
        medications=["aspirin", 123]  # Will catch type error
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Performance Optimizations

### Memory Efficiency
- **Lazy Loading**: Figure data loaded on-demand
- **Optional Fields**: Minimize memory footprint
- **Batch Processing**: Optimized for bulk operations

### Database Integration
- **SQLModel Compatibility**: Direct ORM mapping
- **Index Optimization**: Fields optimized for common queries
- **Bulk Operations**: Efficient batch inserts/updates

## Extension Guidelines

### Adding New Models
1. **Inherit from appropriate base class**
2. **Follow naming conventions** (snake_case for fields)
3. **Add comprehensive field documentation**
4. **Include example data in Config**
5. **Add validation tests**

### Custom Validators


## Integration Points

### Database Layer
- **CRUD Operations**: Direct integration with utils.crud
- **Migration Support**: Schema evolution capabilities
- **Backup/Restore**: Model-aware data export

### AI Processing
- **BioBERT Integration**: Automatic entity extraction
- **OpenAI Services**: Structured output formatting
- **Validation**: AI output validation against schemas

### Search Systems
- **Qdrant Integration**: Vector storage and retrieval
- **Faceted Search**: Multi-field filtering
- **Similarity Queries**: Semantic search capabilities

---

*All models are designed for high-performance biomedical document processing with full type safety and validation.*
embedding = QdrantEmbeddingModel(
    doc_id="123",
    block_id="456",
    embedding=[0.1, 0.2, 0.3]
)
```