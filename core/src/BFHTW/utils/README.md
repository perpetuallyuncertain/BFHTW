# Utilities Module

Essential utility functions and helper classes supporting BFHTW's biomedical document processing capabilities. This module provides foundational services including database operations, document parsing, vector storage, and system logging.

## Overview

The utilities module contains specialized tools organized by function:

- **Database Operations**: CRUD utilities for SQLite and data management
- **Document Processing**: PDF and NXML parsing and text extraction
- **Vector Storage**: Qdrant integration for semantic search
- **System Services**: Logging, caching, and file operations
- **Data Validation**: Quality assurance and format checking

## Module Organization

```
utils/
├── crud/                       # Database CRUD operations
├── db/                         # Database connection and management
├── doc_generator/              # Documentation generation tools
├── io/                         # File I/O and data serialization
├── logs.py                     # Centralized logging system
├── nxml/                       # NXML parsing and processing
├── pdf/                        # PDF text extraction and metadata
├── qdrant/                     # Vector database operations
└── README.md                   # This file
```

## Core Components

### Database Utilities (`crud/`, `db/`)
- **CRUD Operations**: Create, Read, Update, Delete for all models
- **Bulk Processing**: Efficient batch operations for large datasets
- **Connection Management**: SQLite connection pooling and optimization
- **Migration Support**: Database schema evolution and updates

### Document Processing (`pdf/`, `nxml/`)
- **PDF Extraction**: Text, metadata, and figure extraction from PDFs
- **NXML Parsing**: Structured content extraction from biomedical XML
- **Multi-format Support**: Unified interface for different document types
- **Quality Validation**: Content quality assessment and filtering

### Vector Operations (`qdrant/`)
- **Embedding Storage**: High-performance vector database integration
- **Similarity Search**: Semantic similarity queries and ranking
- **Collection Management**: Organized storage by document type and model
- **Batch Operations**: Efficient bulk embedding operations

### System Services (`logs.py`, `io/`)
- **Structured Logging**: JSON-formatted logs with timing metadata
- **File Operations**: Robust file handling with error recovery
- **Caching**: Intelligent caching for frequently accessed data
- **Configuration**: Environment-based configuration management

## Usage Examples

### Database Operations
```python
from BFHTW.utils.crud.crud import CRUD
from BFHTW.models.document_main import Document

# Create new document record
doc = Document(source_db="pubmed_pmc", external_id="PMC123")
CRUD.insert(table='documents', model=Document, data=doc)

# Bulk insert operations
CRUD.bulk_insert(
    table='pdf_blocks',
    model=PDFBlock,
    data_list=extracted_blocks
)

# Query with filtering
results = CRUD.get(
    table='bio_blocks',
    model=BiomedicalEntityBlock,
    id_field='diseases',
    id_value='hepatoblastoma'
)
```

### Document Processing
```python
from BFHTW.utils.pdf.pdf_block_extractor import PDFBlockExtractor
from BFHTW.utils.nxml.nxml_parser import PubMedNXMLParser

# PDF processing
extractor = PDFBlockExtractor()
blocks = extractor.extract_blocks(
    doc_id="doc_123",
    pdf_path="/path/to/article.pdf"
)

# NXML processing  
parser = PubMedNXMLParser(
    file_path="/path/to/article.nxml",
    doc_id="doc_123"
)
metadata = parser.get_document_metadata()
text_blocks = list(parser.extract_blocks())
```

### Vector Database Operations
```python
from BFHTW.utils.qdrant.qdrant_crud import QdrantCRUD
from qdrant_client.models import PointStruct

# Initialize vector database
qdrant = QdrantCRUD(collection_name='bio_blocks')

# Store embeddings
points = [
    PointStruct(
        id=block.block_id,
        vector=embedding.tolist(),
        payload={"doc_id": block.doc_id, "text": block.text}
    )
    for block, embedding in zip(blocks, embeddings)
]
qdrant.upsert_embeddings_bulk(points)

# Semantic search
similar_docs = qdrant.search_similar(
    query_vector=query_embedding,
    limit=10,
    filter_conditions={"doc_type": "clinical_trial"}
)
```

### Logging System
```python
from BFHTW.utils.logs import get_logger

# Initialize logger with retention
logger = get_logger(logger_name="processing", retain=True)

# Structured logging with metadata
logger.info("Processing started", extra={
    "doc_id": "PMC123456",
    "batch_size": 10,
    "processing_time": 45.2
})

# Error tracking with context
try:
    process_document(doc_path)
except Exception as e:
    logger.error("Processing failed", extra={
        "error_type": type(e).__name__,
        "doc_path": str(doc_path),
        "traceback": traceback.format_exc()
    })
```

## Advanced Features

### Bulk Processing Optimization
```python
# Efficient batch operations
from BFHTW.utils.crud.batch_processor import BatchProcessor

processor = BatchProcessor(batch_size=1000)
processor.bulk_insert_with_validation(
    table='keywords',
    model=BiomedicalEntityBlock,
    data_generator=entity_generator(),
    validate_foreign_keys=True
)
```

### Quality Assurance
```python
from BFHTW.utils.validation.content_validator import ContentValidator

validator = ContentValidator()
quality_score = validator.assess_text_quality(
    text=extracted_text,
    min_length=100,
    check_encoding=True,
    biomedical_vocabulary=True
)
```

### Performance Considerations

#### Database Optimization
- **Connection Pooling**: Efficient database connection management
- **Batch Operations**: Bulk inserts/updates for high throughput
- **Index Strategy**: Optimized indexing for common query patterns
- **Transaction Management**: Proper transaction scoping for data integrity

#### Memory Management
- **Streaming Processing**: Handle large documents without memory overflow
- **Garbage Collection**: Explicit cleanup of large objects
- **Batch Size Tuning**: Configurable batch sizes based on available memory
- **Lazy Loading**: Load data on-demand to minimize memory footprint

---

*Comprehensive utilities designed for robust, high-performance biomedical document processing with enterprise-grade reliability and monitoring.*