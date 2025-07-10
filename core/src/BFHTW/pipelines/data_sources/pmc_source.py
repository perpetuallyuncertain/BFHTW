"""
PMC-specific data source implementation.

Integrates existing PMC functionality (API client, file fetchers, mapping)
into the unified data source architecture.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from datetime import datetime
import uuid

from BFHTW.pipelines.data_sources.base_source import BaseDataSource, DataSourceConfig, SearchResult, DownloadInfo
from BFHTW.models.document_main import Document
from BFHTW.sources.pubmed_pmc.pmc_api_client import PMCAPIClient
from BFHTW.sources.pubmed_pmc.fetch.fetch_file_list import FileListFetcher
from BFHTW.sources.pubmed_pmc.fetch.fetch_PMCID_mapping import PMCIDMappingFetcher
from BFHTW.utils.logs import get_logger

L = get_logger()

@dataclass
class PMCConfig(DataSourceConfig):
    """PMC-specific configuration."""
    search_terms_file: str = "search_terms.json"
    api_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    ftp_base_url: str = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/"
    retmax: int = 1_000_000
    retmode: str = "json"
    update_reference_files: bool = True

class PMCDataSource(BaseDataSource):
    """
    PMC-specific data source implementation.
    
    Integrates all existing PMC functionality:
    - API search
    - File list fetching  
    - PMCID mapping
    - Metadata merging
    """
    
    def __init__(self, config: PMCConfig):
        super().__init__(config)
        self.pmc_config = config
        
        # Initialize integrated components
        self.api_client = None
        self.file_fetcher = FileListFetcher()
        self.mapping_fetcher = PMCIDMappingFetcher()
        
        # Cache for merged data
        self._merged_data: Optional[pd.DataFrame] = None
        self._last_update: Optional[datetime] = None
    
    def get_identifier(self) -> str:
        """Return unique identifier for PMC source."""
        return "pmc"
    
    def validate_connection(self) -> bool:
        """Validate connection to PMC services."""
        try:
            # Test API client
            if not self.api_client:
                self._initialize_api_client()
            
            # Test FTP connection by trying to fetch a small file
            import requests
            test_url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/"
            response = requests.head(test_url, timeout=10)
            
            if response.status_code != 200:
                L.error(f"Cannot connect to PMC FTP server, status: {response.status_code}")
                return False
            
            L.info("PMC connection validation successful")
            return True
            
        except Exception as e:
            L.error(f"PMC connection validation failed: {str(e)}")
            return False
    
    def search(self, terms: List[str], max_results: Optional[int] = None) -> List[SearchResult]:
        """
        Search PMC using API client.
        
        Args:
            terms: Search terms
            max_results: Maximum results (uses config if None)
            
        Returns:
            List of SearchResult objects with PMC IDs
        """
        try:
            if not self.api_client:
                self._initialize_api_client()
            
            # Use existing API client search functionality
            # Note: PMCAPIClient expects search terms as a single list
            if self.api_client and hasattr(self.api_client, 'pmc_ids'):
                pmc_ids = self.api_client.pmc_ids
            else:
                L.error("PMC API client not properly initialized")
                return []
            
            max_results = max_results or self.config.max_results
            if len(pmc_ids) > max_results:
                pmc_ids = pmc_ids[:max_results]
            
            # Convert PMC IDs to SearchResult objects
            search_results = []
            for pmc_id in pmc_ids:
                search_results.append(SearchResult(
                    doc_id=pmc_id,
                    source_db="PMC",
                    title=None,  # Will be populated in fetch_metadata
                    url=None,    # Will be populated in get_download_info
                    metadata={"pmcid": pmc_id}
                ))
            
            L.info(f"PMC search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            L.error(f"PMC search failed: {str(e)}")
            return []
    
    def fetch_metadata(self, doc_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch detailed metadata for PMC IDs using merged data.
        
        Args:
            doc_ids: List of PMC IDs
            
        Returns:
            List of metadata dictionaries with merged PMC data
        """
        try:
            # Ensure we have up-to-date merged data
            merged_data = self._get_merged_data()
            
            metadata_list = []
            for doc_id in doc_ids:
                # Find matching record in merged data
                doc_id_clean = doc_id.replace("PMC", "") if doc_id.startswith("PMC") else doc_id
                matches = merged_data[merged_data['PMCID'] == doc_id_clean]
                
                if matches.empty:
                    L.warning(f"No metadata found for PMC ID: {doc_id}")
                    continue
                
                # Take first match and convert to dict
                match = matches.iloc[0]
                metadata = {
                    'pmcid': f"PMC{doc_id_clean}",
                    'pmid_x': match.get('PMID_x'),
                    'pmid_y': match.get('PMID_y'), 
                    'accession_id': match.get('Accession ID'),
                    'file_path': match.get('File'),
                    'license': match.get('License'),
                    'title': None,  # Not available in file lists
                    'ftp_path': match.get('File')  # PMC FTP path
                }
                
                metadata_list.append(metadata)
            
            L.info(f"Retrieved metadata for {len(metadata_list)} PMC documents")
            return metadata_list
            
        except Exception as e:
            L.error(f"Failed to fetch PMC metadata: {str(e)}")
            return []
    
    def get_download_info(self, doc_id: str) -> Optional[DownloadInfo]:
        """
        Get download information for a PMC document.
        
        Args:
            doc_id: PMC ID
            
        Returns:
            DownloadInfo with PMC FTP details
        """
        try:
            # Get metadata for this document
            metadata_list = self.fetch_metadata([doc_id])
            if not metadata_list:
                return None
            
            metadata = metadata_list[0]
            ftp_path = metadata.get('ftp_path')
            if not ftp_path:
                L.warning(f"No FTP path found for PMC ID: {doc_id}")
                return None
            
            # Construct full download URL
            download_url = f"{self.pmc_config.ftp_base_url}{ftp_path}"
            
            # Determine format from file extension
            format_hint = "nxml"  # PMC files are typically NXML in tar.gz
            if ftp_path.lower().endswith('.pdf'):
                format_hint = "pdf"
            
            return DownloadInfo(
                doc_id=doc_id,
                download_url=download_url,
                format_hint=format_hint,
                file_name=ftp_path.split('/')[-1] if '/' in ftp_path else ftp_path,
                metadata=metadata
            )
            
        except Exception as e:
            L.error(f"Failed to get download info for PMC ID {doc_id}: {str(e)}")
            return None
    
    def format_as_document(self, metadata: Dict[str, Any]) -> Document:
        """
        Convert PMC metadata to Document model.
        
        Args:
            metadata: PMC metadata dictionary
            
        Returns:
            Document instance
        """
        return Document(
            doc_id=str(uuid.uuid4()),
            source_db="PMC",
            external_id=metadata.get('pmcid', ''),
            format="nxml",
            title=metadata.get('title'),
            source_file=metadata.get('file_path', '').split('/')[-1] if metadata.get('file_path') else None,
            retrieved_at=None,
            processed=False,
            has_figures=None,
            qdrant_synced=False,
            notes=f"FTP Path: {metadata.get('ftp_path', '')}, License: {metadata.get('license', '')}",
            search_tags=None,
            retrival_context=None,
            ingest_pipeline="pmc_metadata_pipeline",
            license_type=metadata.get('license'),
            publication_date=None,
            authors=None,
            journal=None,
            abstract=None,
            clinical_trial_ref=None,
            doi=None
        )
    
    def update_reference_data(self) -> bool:
        """
        Update PMC reference files (file lists and mappings).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.pmc_config.update_reference_files:
                L.info("PMC reference file update disabled")
                return True
            
            L.info("Updating PMC reference files...")
            
            # Update file list
            file_list_result = self.file_fetcher.fetch_new_articles()
            
            # Update PMCID mapping
            mapping_result = self.mapping_fetcher.fetch()
            
            # Reset cached merged data
            self._merged_data = None
            self._last_update = datetime.now()
            
            L.info("PMC reference files updated successfully")
            return True
            
        except Exception as e:
            L.error(f"Failed to update PMC reference files: {str(e)}")
            return False
    
    def _initialize_api_client(self):
        """Initialize PMC API client with search terms."""
        try:
            self.api_client = PMCAPIClient(
                url=self.pmc_config.api_url,
                search_terms_file_path=self.pmc_config.search_terms_file,
                db="pmc",
                retmax=self.pmc_config.retmax,
                retmode=self.pmc_config.retmode
            )
            L.info("PMC API client initialized")
            
        except Exception as e:
            L.error(f"Failed to initialize PMC API client: {str(e)}")
            raise
    
    def _get_merged_data(self) -> pd.DataFrame:
        """
        Get merged PMC data (file list + PMCID mapping).
        Uses cache if available and recent.
        """
        # Check if we need to refresh cache
        should_refresh = (
            self._merged_data is None or
            self._last_update is None or
            (datetime.now() - self._last_update).total_seconds() > 
            (self.config.update_frequency_hours * 3600)
        )
        
        if should_refresh:
            L.info("Refreshing PMC merged data cache...")
            self._merged_data = self._create_merged_data()
            self._last_update = datetime.now()
        
        return self._merged_data if self._merged_data is not None else pd.DataFrame()
    
    def _create_merged_data(self) -> pd.DataFrame:
        """
        Create merged data from file list and PMCID mapping.
        Integrates logic from merge_article_paths_with_pmids.py
        """
        try:
            cache_dir = self.get_cache_dir()
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            # Load PMC ID mapping (use correct path from fetcher)
            pmid_map_path = Path(self.mapping_fetcher.storage_dir) / f"PMC-ids_{today_str}.csv.gz"
            if not pmid_map_path.exists():
                L.warning(f"PMID mapping file not found: {pmid_map_path}")
                # Try to fetch it
                self.mapping_fetcher.fetch()
                pmid_map_path = Path(self.mapping_fetcher.storage_dir) / f"PMC-ids_{today_str}.csv.gz"
            
            # Load file list (use correct path from fetcher)
            oa_file_list_path = Path(self.file_fetcher.storage_dir) / f"oa_file_list_{today_str}.csv"
            if not oa_file_list_path.exists():
                L.warning(f"File list not found: {oa_file_list_path}")
                # Try to fetch it
                self.file_fetcher.fetch_new_articles()
                oa_file_list_path = Path(self.file_fetcher.storage_dir) / f"oa_file_list_{today_str}.csv"
            
            # Read the files
            pmid_map = pd.read_csv(pmid_map_path, usecols=["PMCID", "PMID"], dtype=str)
            oa_file_list = pd.read_csv(
                oa_file_list_path, 
                usecols=["Accession ID", "File", "PMID", "License"], 
                dtype=str
            )
            
            # Merge the data
            merged = oa_file_list.merge(
                pmid_map, 
                left_on="Accession ID", 
                right_on="PMCID", 
                how="left"
            )
            
            L.info(f"Created merged PMC data with {len(merged)} records")
            return merged
            
        except Exception as e:
            L.error(f"Failed to create merged PMC data: {str(e)}")
            # Return empty DataFrame if merge fails
            return pd.DataFrame()

def create_pmc_source(
    search_terms_file: str = "search_terms.json",
    max_results: int = 1000,
    update_reference_files: bool = True
) -> PMCDataSource:
    """
    Factory function to create PMC data source.
    
    Args:
        search_terms_file: Path to search terms JSON file
        max_results: Maximum search results
        update_reference_files: Whether to update reference files
        
    Returns:
        Configured PMCDataSource instance
    """
    config = PMCConfig(
        name="PMC",
        max_results=max_results,
        search_terms_file=search_terms_file,
        update_reference_files=update_reference_files
    )
    
    return PMCDataSource(config)
