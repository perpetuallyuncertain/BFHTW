"""
Multi-source data source implementations for extensible pipeline architecture.

Provides concrete implementations for various biomedical data sources including
PubMed Central, arXiv, and other repositories.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import json
from abc import ABC

from BFHTW.pipelines.base_pipeline import DataSource
from BFHTW.sources.pubmed_pmc.pmc_api_client import PMCAPIClient
from BFHTW.sources.pubmed_pmc.fetch.fetch_file_list import FileListFetcher
from BFHTW.sources.pubmed_pmc.fetch.fetch_PMCID_mapping import PMCIDMappingFetcher
from BFHTW.sources.pubmed_pmc.fetch.fetch_xml_paths import FetchXML
from BFHTW.utils.logs import get_logger

L = get_logger()

class PubMedCentralSource(DataSource):
    """Data source implementation for PubMed Central."""
    
    def __init__(
        self,
        search_terms_file: Optional[str] = None,
        max_articles: int = 1000,
        update_reference_files: bool = True
    ):
        self.search_terms_file = search_terms_file or "search_terms.json"
        self.max_articles = max_articles
        self.update_reference_files = update_reference_files
        self._connection_validated = False
    
    def get_identifier(self) -> str:
        """Return unique identifier for PMC source."""
        return "pubmed_central"
    
    def validate_connection(self) -> bool:
        """Validate connection to PMC API and services."""
        try:
            # Test PMC API client
            client = PMCAPIClient(
                search_terms_file_path=self.search_terms_file,
                db="pmc"
            )
            
            # Validate search terms file exists
            search_terms_path = Path(self.search_terms_file)
            if not search_terms_path.exists():
                L.error(f"Search terms file not found: {self.search_terms_file}")
                return False
            
            # Test file list fetcher
            file_fetcher = FileListFetcher()
            if not file_fetcher.validate_ftp_connection():
                L.error("Cannot connect to PMC FTP server")
                return False
            
            self._connection_validated = True
            return True
            
        except Exception as e:
            L.error(f"PMC connection validation failed: {str(e)}")
            return False
    
    def fetch_metadata(self) -> List[Dict[str, Any]]:
        """Fetch article metadata from PMC."""
        if not self._connection_validated:
            if not self.validate_connection():
                raise ConnectionError("Cannot establish connection to PMC")
        
        metadata_items = []
        
        try:
            # Step 1: Update reference files if requested
            if self.update_reference_files:
                L.info("Updating PMC reference files...")
                
                file_fetcher = FileListFetcher()
                file_list = file_fetcher.fetch_new_articles()
                
                id_fetcher = PMCIDMappingFetcher()
                id_mapping = id_fetcher.fetch()
                
                L.info(f"Updated reference files: {len(file_list)} file entries, {len(id_mapping)} ID mappings")
            
            # Step 2: Execute search and get article paths
            L.info("Executing PMC search and resolving article paths...")
            
            xml_fetch = FetchXML()
            article_paths = xml_fetch.match_pmcids_to_ftp_paths()
            
            if len(article_paths) > self.max_articles:
                L.info(f"Limiting results to {self.max_articles} articles (found {len(article_paths)})")
                article_paths = article_paths.head(self.max_articles)
            
            # Step 3: Convert to metadata format
            field_mapping = {
                "File": "ftp_path",
                "Accession ID": "accession_id", 
                "PMID_x": "pmid_source",
                "License": "license_type",
                "PMCID": "pmcid",
                "PMID_y": "pmid_mapped"
            }
            
            for _, row in article_paths.iterrows():
                metadata_item = {}
                for source_field, target_field in field_mapping.items():
                    if source_field in row:
                        metadata_item[target_field] = row[source_field]
                
                # Add pipeline metadata
                metadata_item["source_db"] = "pubmed_central"
                metadata_item["full_text_downloaded"] = False
                metadata_item["discovered_at"] = pd.Timestamp.now().isoformat()
                
                metadata_items.append(metadata_item)
            
            L.info(f"Retrieved metadata for {len(metadata_items)} articles from PMC")
            return metadata_items
            
        except Exception as e:
            L.error(f"Failed to fetch PMC metadata: {str(e)}")
            raise

class ArxivSource(DataSource):
    """Data source implementation for arXiv (placeholder for future extension)."""
    
    def __init__(self, search_query: str = "biomedical", max_results: int = 100):
        self.search_query = search_query
        self.max_results = max_results
    
    def get_identifier(self) -> str:
        """Return unique identifier for arXiv source."""
        return "arxiv"
    
    def validate_connection(self) -> bool:
        """Validate connection to arXiv API."""
        # TODO: Implement arXiv connection validation
        L.warning("arXiv source validation not yet implemented")
        return False
    
    def fetch_metadata(self) -> List[Dict[str, Any]]:
        """Fetch metadata from arXiv."""
        # TODO: Implement arXiv metadata fetching
        L.warning("arXiv metadata fetching not yet implemented")
        return []

class LocalFileSource(DataSource):
    """Data source for local file-based datasets."""
    
    def __init__(self, file_path: str, file_format: str = "json"):
        self.file_path = Path(file_path)
        self.file_format = file_format.lower()
    
    def get_identifier(self) -> str:
        """Return unique identifier for local file source."""
        return f"local_file:{self.file_path.name}"
    
    def validate_connection(self) -> bool:
        """Validate that local file exists and is readable."""
        try:
            if not self.file_path.exists():
                L.error(f"Local file does not exist: {self.file_path}")
                return False
            
            if not self.file_path.is_file():
                L.error(f"Path is not a file: {self.file_path}")
                return False
            
            # Test read access
            with open(self.file_path, 'r') as f:
                # Try to read first few bytes
                f.read(100)
            
            return True
            
        except Exception as e:
            L.error(f"Local file validation failed: {str(e)}")
            return False
    
    def fetch_metadata(self) -> List[Dict[str, Any]]:
        """Load data from local file."""
        try:
            if self.file_format == "json":
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                
                # Handle both single objects and arrays
                if isinstance(data, dict):
                    return [data]
                elif isinstance(data, list):
                    return data
                else:
                    raise ValueError(f"Unexpected JSON structure: {type(data)}")
            
            elif self.file_format in ["csv", "tsv"]:
                separator = "," if self.file_format == "csv" else "\t"
                df = pd.read_csv(self.file_path, sep=separator)
                return df.to_dict('records')
            
            else:
                raise ValueError(f"Unsupported file format: {self.file_format}")
                
        except Exception as e:
            L.error(f"Failed to load local file {self.file_path}: {str(e)}")
            raise

class DatabaseSource(DataSource):
    """Data source for existing database tables."""
    
    def __init__(self, table_name: str, query_conditions: Optional[Dict[str, Any]] = None):
        self.table_name = table_name
        self.query_conditions = query_conditions or {}
    
    def get_identifier(self) -> str:
        """Return unique identifier for database source."""
        return f"database:{self.table_name}"
    
    def validate_connection(self) -> bool:
        """Validate database connection and table existence."""
        try:
            from BFHTW.utils.crud.crud import CRUD
            
            # Test basic database connection by attempting a simple query
            # This is a simplified check - could be enhanced with table schema validation
            result = CRUD.get(
                table=self.table_name,
                model=None,  # We'll handle the model validation elsewhere
                ALL=True
            )
            
            return True
            
        except Exception as e:
            L.error(f"Database source validation failed for table {self.table_name}: {str(e)}")
            return False
    
    def fetch_metadata(self) -> List[Dict[str, Any]]:
        """Fetch data from database table."""
        try:
            from BFHTW.utils.crud.crud import CRUD
            
            # TODO: Implement query conditions filtering
            # For now, get all records (this should be enhanced for production use)
            results = CRUD.get(
                table=self.table_name,
                model=None,  # Model will be handled by the pipeline
                ALL=True
            )
            
            # Convert to list of dictionaries
            if hasattr(results, 'to_dict'):
                return results.to_dict('records')
            elif isinstance(results, list):
                return [item.model_dump() if hasattr(item, 'model_dump') else item for item in results]
            else:
                return []
                
        except Exception as e:
            L.error(f"Failed to fetch data from database table {self.table_name}: {str(e)}")
            raise

# Factory function for easy data source creation
def create_data_source(source_type: str, **kwargs) -> DataSource:
    """
    Factory function to create data sources.
    
    Args:
        source_type: Type of data source ('pmc', 'arxiv', 'local_file', 'database')
        **kwargs: Source-specific parameters
    
    Returns:
        Configured DataSource instance
    """
    sources = {
        'pmc': PubMedCentralSource,
        'pubmed_central': PubMedCentralSource,
        'arxiv': ArxivSource,
        'local_file': LocalFileSource,
        'database': DatabaseSource
    }
    
    if source_type not in sources:
        raise ValueError(f"Unknown source type: {source_type}. Available: {list(sources.keys())}")
    
    return sources[source_type](**kwargs)
