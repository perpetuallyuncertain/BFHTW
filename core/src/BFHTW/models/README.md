# Biomedical Document Processing Models

This repository contains a set of Pydantic models designed for processing and managing biomedical documents. The models facilitate the extraction, representation, and storage of metadata and text blocks from various document formats, including PDF and NXML. The primary goal is to support the ingestion, indexing, and searching of biomedical literature.

## Table of Contents
- [Models Overview](#models-overview)
- [Folder Structure](#folder-structure)
- [Usage](#usage)
- [License](#license)

## Models Overview
The following models are included in this repository:

1. **QdrantEmbeddingModel**: Represents a vector embedding for a document block, suitable for insertion into Qdrant, a vector search engine.
2. **BlockBase**: A base model for all document text blocks, including standard fields such as text content, location, and processing status.
3. **BiomedicalEntityBlock**: Captures structured data for biological entities extracted from document blocks, facilitating faceted search and metadata cross-referencing.
4. **PMCArticleMetadata**: Contains metadata for PMC (PubMed Central) articles, linking open-access archives with PubMed identifiers.
5. **MetaBase**: A base metadata model common to all document types, containing fields for document identification and basic attributes.
6. **Document**: The master metadata record for biomedical documents, linking to various models and facilitating audit and search capabilities.
7. **NXMLBlock**: An extension of BlockBase for NXML documents, focusing on structured content with section semantics.
8. **NXMLMetadata**: Extended metadata model for NXML documents, inheriting fields from MetaBase and adding NXML-specific attributes.
9. **PDFBlock**: An extension of BlockBase for PDF documents, including layout and font metadata.
10. **PDFMetadata**: Extended metadata model for PDF documents, inheriting from MetaBase and adding PDF-specific fields.

## Folder Structure
The folder structure is as follows:
```
BFHTW/
│
├── models/
│   ├── block_model.py           # Base model for document blocks
│   ├── bio_medical_entity_block.py  # Model for biomedical entity filters
│   ├── meta_model.py            # Base metadata model
│   ├── document_main.py         # Master metadata record for documents
│   ├── nxml_models.py           # Models specific to NXML documents
│   ├── pdf_models.py            # Models specific to PDF documents
│   ├── qdrant.py                # Model for Qdrant embeddings
│   └── pubmed_pmc.py            # Model for PMC article metadata
└── ...                           # Other components and utilities
```

## Usage
To use these models, import the relevant classes from the module. For example:
```python
from BFHTW.models.qdrant import QdrantEmbeddingModel
from BFHTW.models.block_model import BlockBase
```

Instantiate the models with the required data:
```python
embedding = QdrantEmbeddingModel(
    doc_id="123",
    block_id="456",
    embedding=[0.1, 0.2, 0.3]
)
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.