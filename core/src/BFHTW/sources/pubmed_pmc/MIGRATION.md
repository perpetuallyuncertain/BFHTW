# PMC Data Source Migration Guide

This directory contains legacy PMC data source functionality that has been migrated to the unified pipeline architecture.

## Migration Status

### ✅ Migrated Components

- **PMC API Client** (`pmc_api_client.py`) → Integrated into `BFHTW.pipelines.data_sources.pmc_source.PMCDataSource`
- **Data Merging** (`merge_article_paths_with_pmids.py`) → Integrated into `PMCDataSource._get_merged_data()`
- **File Fetchers** (`fetch/`) → Integrated into `PMCDataSource` for reference file updates

### 🔄 New Unified Architecture

The new architecture provides:

1. **Unified Interface**: All data sources (PMC, arXiv, etc.) implement the same `BaseDataSource` contract
2. **Centralized Registry**: Data sources are registered and managed through `DataSourceRegistry`
3. **Consistent Validation**: All data sources use the same validation and error handling patterns
4. **Document Model**: All metadata flows through the unified `Document` model
5. **Pipeline Integration**: Seamless integration with the pipeline framework

### 📖 Usage Examples

#### Old Way (Deprecated)
```python
from BFHTW.sources.pubmed_pmc.merge_article_paths_with_pmids import join_mapping_files
from BFHTW.sources.pubmed_pmc.pmc_api_client import PMCAPIClient

# Old fragmented approach
merged_data = join_mapping_files()
api_client = PMCAPIClient(...)
```

#### New Way (Recommended)
```python
from BFHTW.pipelines.data_sources.pmc_source import create_pmc_source
from BFHTW.pipelines.data_sources.registry import get_source

# Using factory function
pmc_source = create_pmc_source(max_results=1000)

# Or using registry
pmc_source = get_source("pmc")

# Unified interface
search_results = pmc_source.search(["cancer", "treatment"])
metadata = pmc_source.fetch_metadata([result.doc_id for result in search_results])
documents = [pmc_source.format_as_document(meta) for meta in metadata]
```

### 🔧 Pipeline Integration

The new architecture integrates with the pipeline framework:

```python
from BFHTW.pipelines.pubmed_pmc.pubmed_metadata_pipeline import PubMedMetadataPipeline

# Pipeline automatically uses the unified data source
pipeline = PubMedMetadataPipeline()
result = pipeline.run()
```

### 🗂️ Data Flow

1. **Search**: Data sources search their respective databases
2. **Metadata**: Fetch detailed metadata for found documents
3. **Document Creation**: Convert metadata to unified `Document` model
4. **Storage**: Save to `documents` table (single source of truth)
5. **Processing**: Document processing pipeline handles all document types

### 📋 Migration Checklist

- [x] Create unified `BaseDataSource` interface
- [x] Implement `PMCDataSource` with integrated functionality
- [x] Create `DataSourceRegistry` for centralized management
- [x] Update `PubMedMetadataPipeline` to use unified interface
- [x] Integrate with `PipelineManager`
- [x] Add deprecation warnings to legacy code
- [x] Create migration documentation

### 🚨 Deprecation Notice

The following files are deprecated and will be removed in a future version:

- `merge_article_paths_with_pmids.py` - Use `PMCDataSource._get_merged_data()`
- Direct usage of `pmc_api_client.py` - Use `PMCDataSource.search()`
- Direct usage of `fetch/` modules - Use `PMCDataSource.update_reference_data()`

### 🔮 Future Enhancements

The unified architecture enables:

- **ArXiv Data Source**: Easily add arXiv support using the same interface
- **Custom Sources**: Add organization-specific data sources
- **Enhanced Validation**: Consistent data quality across all sources
- **Scalable Processing**: Unified pipeline handles all document types
- **Monitoring**: Centralized tracking of all data source operations

### 🆘 Support

If you encounter issues during migration, check:

1. **Error Logs**: The new architecture provides detailed logging
2. **Validation**: Use `data_source.validate_connection()` to test connections
3. **Registry**: Use `get_registry().list_sources()` to see available sources
4. **Documentation**: Check the class docstrings for detailed usage examples

For questions or issues, please refer to the main project documentation or create an issue in the project repository.
