# Processing Pipelines

Automated workflows for biomedical document ingestion, processing, and analysis. These pipelines orchestrate the complete journey from article discovery to structured clinical insights, leveraging AI models and vector databases for comprehensive literature analysis.

## Overview

The pipelines module implements the core processing workflows that transform raw biomedical literature into structured, searchable data:

- **Metadata Fetching**: Automated discovery and cataloging of relevant articles
- **Document Processing**: Full-text download, extraction, and parsing
- **AI Analysis**: Named entity recognition and embedding generation  
- **Quality Assurance**: Validation, error handling, and audit logging

## Pipeline Architecture

```
 Article Discovery →  Metadata Extraction →  Document Download
                                                           ↓
 Semantic Search ←  AI Analysis ←  Text Extraction ←  Content Parse
```

## Core Pipelines

### 1. Metadata Fetching Pipeline (`pubmed_fetch_metadata.py`)

**Purpose**: Discovers and catalogs articles from PubMed Central for processing

**Workflow**:
1. **Reference Data Update**: Downloads latest PMC file lists and ID mappings
2. **Search Execution**: Queries PMC API using configured search terms
3. **Path Resolution**: Maps article IDs to downloadable file paths
4. **Database Storage**: Saves metadata for downstream processing

**Key Features**:
- Incremental updates (only new articles)
- Configurable search terms (`search_terms.json`)
- Automatic retry logic for API failures
- Comprehensive metadata validation

**Usage**:
```python
from BFHTW.pipelines.pubmed_fetch_metadata import run_metadata_pipeline

# Fetch latest articles matching search criteria
results = run_metadata_pipeline(
    search_terms_file="search_terms.json",
    max_articles=1000
)
```

### 2. Document Processing Pipeline (`pubmed_download_and_parse.py`)

**Purpose**: Downloads, processes, and analyzes full-text articles

**Workflow**:
1. **Queue Management**: Retrieves unprocessed articles from database
2. **Content Download**: Fetches TAR.GZ archives from PMC FTP
3. **Format Detection**: Identifies PDF/NXML content types
4. **Text Extraction**: Parses documents into structured blocks
5. **AI Analysis**: Applies NER and generates embeddings
6. **Storage**: Saves results to database and vector store
7. **Cleanup**: Manages temporary files and processing state

**Key Features**:
- Multi-format support (PDF, NXML)
- Parallel processing capabilities
- Robust error handling and recovery
- Automatic figure extraction and caching
- BioBERT integration for biomedical NER
- Qdrant vector database integration

**Usage**:
```python
from BFHTW.pipelines.pubmed_download_and_parse import run_processing_pipeline

# Process next batch of articles
results = run_processing_pipeline(
    batch_size=10,
    max_concurrent=3,
    include_figures=True
)
```

## Detailed Processing Steps

### Metadata Pipeline Stages

1. **Reference File Updates**
   ```python
   # Download latest PMC reference data
   file_list = FileListFetcher().fetch_new_articles()
   id_mapping = PMCIDMappingFetcher().fetch()
   ```

2. **Search Term Processing** 
   ```python
   # Configure hepatoblastoma-specific search
   search_terms = {
       "hepatoblastoma": ["hepatoblastoma", "liver cancer pediatric"],
       "treatments": ["cisplatin", "doxorubicin", "liver transplant"],
       "resistance": ["refractory", "drug resistance"]
   }
   ```

3. **Article Discovery**
   ```python
   # Execute PMC API searches
   xml_fetch = FetchXML()
   article_paths = xml_fetch.match_pmcids_to_ftp_paths()
   ```

4. **Database Integration**
   ```python
   # Store metadata for processing
   CRUD.bulk_insert(
       table='pubmed_fulltext_links',
       model=PMCArticleMetadata,
       data_list=article_metadata
   )
   ```

### Document Processing Stages

1. **Download Management**
   ```python
   # Parallel download with error handling
   fetcher = TarballFetcher()
   tarball_path = fetcher.download(full_url, target_path)
   extracted_path = fetcher.extract(tarball_path)
   ```

2. **Content Parsing**
   ```python
   # Multi-format document parsing
   if pdf_path:
       pdf_meta = PDFReadMeta().extract_metadata(pdf_path)
       blocks = PDFBlockExtractor().extract_blocks(pdf_path)
   elif nxml_path:
       nxml_parser = PubMedNXMLParser(nxml_path)
       blocks = list(nxml_parser.extract_blocks())
   ```

3. **AI Analysis**
   ```python
   # Biomedical entity recognition
   ner = BioBERTNER()
   entities = [ner.run(block.text) for block in blocks]
   
   # Semantic embedding generation
   embedder = BioBERTEmbedder()
   embeddings = [embedder.run(block.text) for block in blocks]
   ```

4. **Vector Storage**
   ```python
   # Store in Qdrant for semantic search
   qdrant_client = QdrantCRUD(collection_name='bio_blocks')
   qdrant_client.upsert_embeddings_bulk(embedding_points)
   ```

## Configuration

### Search Terms (`search_terms.json`)
```json
{
  "hepatoblastoma": [
    "hepatoblastoma",
    "hepatic tumor pediatric",
    "liver cancer children"
  ],
  "treatment_modalities": [
    "cisplatin hepatoblastoma",
    "liver transplant pediatric",
    "chemotherapy liver tumor"
  ],
  "resistance_mechanisms": [
    "refractory hepatoblastoma",
    "drug resistance liver",
    "salvage therapy"
  ]
}
```

search_terms.json is currently broad to capture higher volumes of clinical research data for comparison and embedding.

### Pipeline Configuration

## Performance Optimization

### Processing Efficiency
- **Batch Processing**: Process multiple articles simultaneously
- **Incremental Updates**: Only process new articles since last run
- **Memory Management**: Cleanup temporary files after processing
- **Error Recovery**: Resume processing from last successful checkpoint

### Resource Management


## Monitoring and Logging

### Processing Metrics
- **Articles Processed**: Total and per-hour rates
- **Success/Failure Rates**: Download and parsing statistics  
- **Entity Extraction**: NER accuracy and coverage
- **Storage Efficiency**: Database and vector store metrics

### Error Handling

## Quality Assurance

### Data Validation
- **Schema Compliance**: All outputs validated against Pydantic models
- **Content Quality**: Text extraction quality checks
- **Entity Accuracy**: NER confidence thresholds
- **Embedding Quality**: Vector similarity validation

### Audit Trail

## Integration with BFHTW Components

### Database Integration
- **SQLite Storage**: Structured metadata and text blocks
- **CRUD Operations**: Efficient bulk insert/update operations
- **Foreign Key Integrity**: Maintained across all tables

### Vector Database
- **Qdrant Collections**: Organized by document type and analysis method
- **Semantic Search**: BioBERT embeddings for similarity queries
- **Filtering**: Combined vector and metadata filtering

### AI Services
- **BioBERT Models**: Local inference for NER and embeddings
- **OpenAI Integration**: Advanced reasoning for complex extractions
- **Model Versioning**: Track AI model versions in metadata

## Usage Examples

### Running Complete Pipeline
```bash
# Full pipeline execution
cd /home/steven/BFHTW/core/src
python -m BFHTW.pipelines.pubmed_fetch_metadata
python -m BFHTW.pipelines.pubmed_download_and_parse
```

### Custom Processing


## Troubleshooting

### Common Issues
- **API Rate Limits**: Built-in backoff and retry logic
- **Disk Space**: Automatic cleanup of temporary files
- **Memory Usage**: Configurable batch sizes for large documents
- **Network Timeouts**: Robust error handling and resume capabilities

### Performance Tuning
- **Concurrent Downloads**: Adjust based on network capacity
- **Batch Sizes**: Optimize for available memory
- **Model Loading**: Cache models to avoid reload overhead
- **Database Connections**: Connection pooling for high throughput

---

*Designed for reliable, high-throughput processing of biomedical literature with comprehensive error handling and quality assurance.*

- NCBI for providing the PubMed Central database.
- The developers and contributors to the BioBERT framework.