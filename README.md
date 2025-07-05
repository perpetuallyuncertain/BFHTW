# BFHTW - Biomedical Framework for Textual Health Workflows

> **RAG AI Model with BioBERT analyzed corpus and OpenAI assistants for biomedical literature processing**

[![Python 3.11+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

BFHTW is a comprehensive AI-powered platform for processing, analyzing, and extracting structured insights from biomedical literature. Specifically designed for hepatoblastoma research, the system combines advanced NLP techniques with vector databases to enable semantic search and clinical data extraction from PubMed Central articles.

## Project Vision

Transform unstructured biomedical literature into actionable clinical insights by:
- **Automated Literature Processing**: Download and parse articles from PubMed Central
- **Biomedical NER**: Extract medications, diseases, symptoms, and clinical markers
- **Semantic Search**: Vector-based similarity search using BioBERT embeddings  
- **Clinical Intelligence**: Structured extraction of treatment outcomes and patient characteristics
- **Research Acceleration**: Enable rapid literature review and meta-analysis for hepatoblastoma research

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         BFHTW Platform                         │
├─────────────────────────────────────────────────────────────────┤
│     Data Sources     │     AI Processing    │      Query Layer    │
│  ├─ PubMed Central   │  ├─ BioBERT NER      │  ├─ Semantic Search │
│  ├─ PMC API          │  ├─ OpenAI Assistants│  ├─ Faceted Search  │
│  └─ FTP Archives     │  └─ Vector Embeddings│  └─ Clinical Queries│
├─────────────────────────────────────────────────────────────────┤
│      Storage Layer                                              │
│  ├─ SQLite (Metadata & Structure)  ├─ Qdrant (Vector Search)    │
│  ├─ Hybrid Figure Storage         └─ Local Cache                │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
BFHTW/
├── core/                           # Core application code
│   ├── src/                        # Source code (see src/README.md for details)
│   │   ├── BFHTW/                  # Main Python package
│   │   │   ├── ai_assistants/      # AI-powered analysis modules
│   │   │   ├── app/                # Web application interface
│   │   │   ├── data/               # Local databases and storage
│   │   │   ├── infrastructure/     # Deployment and infrastructure
│   │   │   ├── models/             # Pydantic data models
│   │   │   ├── pipelines/          # Data processing workflows
│   │   │   ├── sources/            # External data integrations
│   │   │   ├── tests/              # Test suites
│   │   │   └── utils/              # Utility functions and helpers
│   │   ├── biomed_schema.png       # Database schema diagram
│   │   └── README.md               # Detailed source documentation
│   ├── libexec/                    # Executable scripts
│   ├── requirements/               # Dependency specifications
│   ├── qdrant_storage/             # Vector database storage
│   └── docs/                       # Project documentation
└── README.md                       # This file
```

## Quick Start

### Prerequisites
- **Python 3.11+** with pip
- **Git** for version control
- **Internet connection** for downloading articles
- **Optional**: Docker for containerized deployment

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BFHTW
   ```

2. **Install dependencies**
   ```bash
   pip install -r core/requirements/base.txt
   ```

3. **Configure search terms** (Optional - defaults provided)
   ```bash
   # Edit search criteria for article discovery
   nano core/src/BFHTW/sources/pubmed_pmc/search_terms.json
   ```

4. **Set up environment** (if using cloud services)
   ```bash
   # Configure API keys and credentials
   source core/src/BFHTW/infrastructure/sh/save_env.sh
   ```

### Basic Usage

#### 1. Fetch Article Metadata
```python
from BFHTW.pipelines import pubmed_fetch_metadata

# Downloads latest PMC file lists and article metadata
# Saves to: core/src/BFHTW/data/database.db
```

#### 2. Process Articles
```python
from BFHTW.pipelines import pubmed_download_and_parse

# Downloads, extracts, and processes articles
# Generates embeddings and extracts biomedical entities
```

#### 3. Query Clinical Data
```python
from BFHTW.utils.crud.crud import CRUD
from BFHTW.models.bio_medical_entity_block import BiomedicalEntityBlock

# Find articles mentioning specific medications
results = CRUD.get(
    table='bio_blocks',
    model=BiomedicalEntityBlock,
    id_field='medications',
    id_value='cisplatin'
)
```

## Core Features

### Document Processing
- **Multi-format Support**: PDF and NXML parsing
- **Metadata Extraction**: Authors, journals, publication dates, DOIs
- **Text Segmentation**: Intelligent block-level text extraction
- **Figure Handling**: Hybrid storage with lazy-loading for optimal performance

### AI-Powered Analysis
- **BioBERT Integration**: State-of-the-art biomedical language model
- **Named Entity Recognition**: Automatic extraction of:
  - Medications and drugs
  - Diseases and disorders  
  - Clinical symptoms
  - Therapeutic procedures
  - Molecular pathways
- **Vector Embeddings**: Semantic similarity search
- **Clinical Intelligence**: Structured extraction of treatment outcomes

### Advanced Search Capabilities
- **Semantic Search**: Find conceptually similar content
- **Faceted Search**: Filter by entity types, publication dates, journals
- **Clinical Queries**: Search for specific treatment regimens, outcomes
- **Cross-Reference**: Link entities across documents

### Data Models

The system uses a robust relational schema optimized for biomedical research:

```sql
-- Core entities with foreign key relationships
documents (doc_id PK) ← blocks (block_id PK, doc_id FK)
                     ← keyword_mentions (block_id FK, doc_id FK)
                     ← figure_metadata (fig_id PK, doc_id FK)
                     ← raw_pdf_metadata (doc_id FK)
                     ← raw_nxml_metadata (doc_id FK)
                     ← processing_log (doc_id FK)
```

See `core/src/biomed_schema.png` for the complete database relationship diagram.

## Research Applications

### Hepatoblastoma Research Focus
- **Treatment Efficacy**: Track chemotherapy regimens and outcomes
- **Resistance Mechanisms**: Identify refractory disease patterns
- **Clinical Markers**: Monitor biomarkers and molecular pathways
- **Surgical Outcomes**: Analyze transplant and resection results
- **Alternative Therapies**: Discover novel treatment approaches

### Extensible Framework
While optimized for hepatoblastoma, BFHTW can be adapted for:
- Other pediatric cancers
- Oncology research in general
- Clinical trial analysis
- Drug discovery research
- Biomarker identification

## Development

### Testing
```bash
# Run full test suite
cd core/src
pytest tests/

# Run specific components
pytest tests/db/          # Database operations
pytest tests/pubmed_pmc/  # PMC integration
```

### Adding New Data Sources
1. Create fetcher class in `sources/`
2. Add corresponding Pydantic models in `models/`
3. Update pipeline in `pipelines/`
4. Add tests in `tests/`

### Extending AI Capabilities
1. Add new assistant in `ai_assistants/internal/` or `ai_assistants/external/`
2. Update extraction models in `models/`
3. Integrate into processing pipeline
4. Configure in `ai_assistants/system_prompt.txt`

## Performance & Scalability

### Current Capabilities
- **Processing Speed**: ~100 articles/hour (depends on article size and complexity)
- **Storage Efficiency**: Hybrid figure storage reduces local storage by 70%
- **Search Performance**: Sub-second semantic search on 10k+ documents
- **Memory Usage**: Optimized for local development environments

### Scaling Options
- **Horizontal Scaling**: Multi-worker processing with job queues
- **Cloud Deployment**: Docker containers with managed databases
- **Performance Tuning**: Batch processing and caching optimizations

## Contributing

We welcome contributions to enhance BFHTW's capabilities:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow existing code structure and naming conventions
- Add comprehensive tests for new features
- Update documentation for API changes
- Use Pydantic models for all data structures
- Include proper logging in processing pipelines

## Documentation

- **Source Code**: [src/README.md](core/src/README.md) - Detailed technical documentation
- **AI Assistants**: [ai_assistants/README.md](core/src/BFHTW/ai_assistants/README.md) - Clinical extraction guides
- **Data Models**: [models/README.md](core/src/BFHTW/models/README.md) - Schema documentation
- **Pipelines**: [pipelines/README.md](core/src/BFHTW/pipelines/README.md) - Processing workflows
- **API Reference**: [docs/reference/](core/docs/reference/) - Generated API docs

## Dependencies

### Core Requirements
- **pydantic**: Data validation and serialization
- **pandas**: Data manipulation and analysis
- **sqlmodel**: Database ORM with Pydantic integration
- **qdrant-client**: Vector database client
- **transformers**: BioBERT model integration
- **openai**: External AI service integration

### Document Processing
- **pymupdf**: PDF text extraction
- **lxml**: NXML parsing
- **trafilatura**: Web content extraction

### External Services
- **azure-data-tables**: Cloud storage integration
- **feedparser**: RSS/Atom feed parsing
- **playwright**: Web automation for complex downloads

See [requirements/base.txt](core/requirements/base.txt) for complete dependency list.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NCBI/NIH** for providing open access to PubMed Central
- **BioBERT Team** for the pre-trained biomedical language model
- **Qdrant** for the efficient vector database solution
- **OpenAI** for language model capabilities
- **The broader biomedical research community** for open science initiatives

## Support

For questions, issues, or contributions:
- **Bug Reports**: Open an issue on GitHub
- **Feature Requests**: Create a feature request issue
- **Documentation**: Check existing docs or open a documentation issue
- **Discussions**: Use GitHub Discussions for general questions

---

**Built with ❤️ for the biomedical research community**

for Mackenzie.
