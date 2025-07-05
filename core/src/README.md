# BFHTW Core Source Code

This directory contains the core implementation of BFHTW (Biomedical Framework for Textual Health Workflows), a comprehensive system for processing, analyzing, and extracting insights from biomedical literature, with a specific focus on hepatoblastoma research.

## Overview

BFHTW is a RAG (Retrieval-Augmented Generation) AI system that combines BioBERT analysis with OpenAI assistants to process biomedical documents from sources like PubMed Central (PMC). The system provides structured extraction of clinical insights, molecular pathways, treatment outcomes, and patient characteristics from scientific literature.

## Directory Structure

```
src/
├── BFHTW/                          # Main package directory
│   ├── ai_assistants/              # AI-powered analysis and extraction
│   │   ├── base/                   # Base AI assistant classes
│   │   ├── external/               # External AI service integrations
│   │   ├── internal/               # Internal AI models (BioBERT, etc.)
│   │   ├── system_prompt.txt       # Clinical extraction prompt
│   │   └── README.md              # AI assistants documentation
│   ├── app/                        # Application layer (web interfaces, APIs)
│   ├── data/                       # Local data storage and databases
│   │   └── database.db            # SQLite database
│   ├── infrastructure/             # Infrastructure and deployment utilities
│   │   ├── sh/                    # Shell scripts for deployment
│   │   └── README.md              # Infrastructure documentation
│   ├── models/                     # Pydantic data models
│   │   ├── bio_medical_entity_block.py  # Biomedical entity extraction model
│   │   ├── block_model.py         # Base block model for text extraction
│   │   ├── document_main.py       # Master document metadata model
│   │   ├── figure_metadata.py     # Figure metadata with hybrid storage
│   │   ├── meta_model.py          # Base metadata model
│   │   ├── nxml_models.py         # NXML-specific document models
│   │   ├── pdf_models.py          # PDF-specific document models
│   │   ├── pubmed_pmc.py          # PMC article metadata
│   │   ├── qdrant.py              # Vector database models
│   │   └── README.md              # Data models documentation
│   ├── pipelines/                  # Data processing pipelines
│   │   ├── pubmed_download_and_parse.py  # Article download and processing
│   │   ├── pubmed_fetch_metadata.py      # Metadata extraction pipeline
│   │   └── README.md              # Pipeline documentation
│   ├── sources/                    # External data source integrations
│   │   └── pubmed_pmc/            # PubMed Central integration
│   │       ├── fetch/             # Data fetching utilities
│   │       ├── pmc_api_client.py  # PMC API client
│   │       ├── search_terms.json  # Search criteria for articles
│   │       └── README.md          # PMC integration documentation
│   ├── tests/                      # Test suites
│   │   ├── db/                    # Database operation tests
│   │   ├── pubmed_pmc/            # PMC integration tests
│   │   └── README.md              # Testing documentation
│   └── utils/                      # Utility modules
│       ├── db/                    # Database utilities and CRUD operations
│       ├── nxml/                  # NXML parsing utilities
│       ├── pdf/                   # PDF processing utilities
│       ├── qdrant/                # Vector database utilities
│       └── logs.py                # Logging configuration
├── biomed_schema.png              # Database schema diagram
├── structure.txt                  # Project structure documentation
├── test_nxml.txt                  # Sample NXML test data
└── README.md                      # This file
```

## Key Components

### AI Assistants (`ai_assistants/`)
- **BioBERT Integration**: Named Entity Recognition and embedding generation
- **Clinical Extraction**: Structured extraction of treatment outcomes, molecular pathways, and patient characteristics
- **External AI Services**: OpenAI API integration for advanced text analysis

### Data Models (`models/`)
- **Document Processing**: Models for PDF, NXML, and generic document metadata
- **Biomedical Entities**: Structured models for medications, diseases, symptoms, and clinical markers
- **Vector Storage**: Integration with Qdrant for semantic search capabilities
- **Hybrid Figure Storage**: Efficient figure metadata with lazy-loading caching

### Processing Pipelines (`pipelines/`)
- **Metadata Fetching**: Automated retrieval of article metadata from PMC
- **Document Processing**: Download, extraction, and analysis of full-text articles
- **NER and Embedding**: Biomedical named entity recognition and vector generation

### Data Sources (`sources/`)
- **PubMed Central**: API integration for article discovery and download
- **Search Configuration**: Configurable search terms for hepatoblastoma research
- **FTP Integration**: Direct access to PMC's open-access archive

### Utilities (`utils/`)
- **Database Operations**: CRUD utilities for SQLite operations
- **Document Parsing**: PDF and NXML text extraction
- **Vector Operations**: Qdrant database management
- **Logging**: Centralized logging configuration

## Database Schema

The system uses a relational database schema optimized for biomedical document processing:

- **documents**: Master document registry
- **blocks**: Text blocks extracted from documents
- **raw_pdf_metadata** / **raw_nxml_metadata**: Format-specific metadata
- **figure_metadata**: Figure references with hybrid storage strategy
- **keyword_mentions**: Biomedical entity mentions with position tracking
- **processing_log**: Audit trail for all processing operations

See `biomed_schema.png` for the complete database relationship diagram.

## Getting Started

### Prerequisites
- Python 3.8+
- Dependencies listed in `../requirements/base.txt`
- SQLite database (automatically created)
- Optional: Qdrant vector database for semantic search

### Installation
```bash
# Install dependencies
pip install -r ../requirements/base.txt

# Configure environment variables (see infrastructure/README.md)
# Set up search terms in sources/pubmed_pmc/search_terms.json
```

### Basic Usage
```python
# Fetch article metadata
from BFHTW.pipelines.pubmed_fetch_metadata import *

# Process downloaded articles
from BFHTW.pipelines.pubmed_download_and_parse import *

# Query biomedical entities
from BFHTW.utils.crud.crud import CRUD
from BFHTW.models.bio_medical_entity_block import BiomedicalEntityBlock

entities = CRUD.get(
    table='bio_blocks',
    model=BiomedicalEntityBlock,
    id_field='diseases',
    id_value='hepatoblastoma'
)
```

## Testing

The project includes comprehensive test suites:

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/db/          # Database operations
pytest tests/pubmed_pmc/  # PMC integration
```

## Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate Pydantic models for new data types
3. Include comprehensive logging in all processing pipelines
4. Add tests for new functionality
5. Update documentation for any API changes

## License

This project is licensed under the MIT License. See the LICENSE file for details.
