"""
Base data source contracts for unified pipeline architecture.

Provides abstract base classes and interfaces for all data sources,
ensuring consistency and scalability across different sources.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import uuid

from BFHTW.models.document_main import Document
from BFHTW.utils.logs import get_logger

L = get_logger()

@dataclass
class DataSourceConfig:
    """Base configuration for data sources."""
    name: str
    enabled: bool = True
    max_results: int = 1000
    cache_dir: Optional[str] = None
    update_frequency_hours: int = 24

@dataclass
class SearchResult:
    """Result from data source search."""
    doc_id: str
    source_db: str
    title: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DownloadInfo:
    """Information needed to download a document."""
    doc_id: str
    download_url: str
    format_hint: str  # "pdf", "nxml", etc.
    file_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseDataSource(ABC):
    """
    Abstract base class for all data sources.
    
    Provides a unified interface for searching, fetching metadata,
    and downloading documents from any source (PMC, arXiv, etc.).
    """
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.name = config.name
        
    @abstractmethod
    def get_identifier(self) -> str:
        """Return unique identifier for this data source."""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate connection to data source."""
        pass
    
    @abstractmethod
    def search(self, terms: List[str], max_results: Optional[int] = None) -> List[SearchResult]:
        """
        Search for documents using search terms.
        
        Args:
            terms: List of search terms
            max_results: Maximum number of results (uses config default if None)
            
        Returns:
            List of SearchResult objects
        """
        pass
    
    @abstractmethod
    def fetch_metadata(self, doc_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch detailed metadata for document IDs.
        
        Args:
            doc_ids: List of document IDs from search results
            
        Returns:
            List of metadata dictionaries
        """
        pass
    
    @abstractmethod
    def get_download_info(self, doc_id: str) -> Optional[DownloadInfo]:
        """
        Get download information for a specific document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            DownloadInfo object or None if not available
        """
        pass
    
    @abstractmethod
    def format_as_document(self, metadata: Dict[str, Any]) -> Document:
        """
        Convert raw metadata to Document model.
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Document instance
        """
        pass
    
    def update_reference_data(self) -> bool:
        """
        Update reference data (file lists, mappings, etc.).
        Default implementation returns True (no-op).
        """
        L.info(f"No reference data update needed for {self.name}")
        return True
    
    def get_cache_dir(self) -> Path:
        """Get cache directory for this data source."""
        if self.config.cache_dir:
            cache_dir = Path(self.config.cache_dir)
        else:
            base_dir = Path(__file__).parents[3]
            cache_dir = base_dir / "sources" / self.name.lower() / "data"
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

class DataSourceRegistry:
    """Registry for managing multiple data sources."""
    
    def __init__(self):
        self._sources: Dict[str, BaseDataSource] = {}
    
    def register(self, source: BaseDataSource):
        """Register a data source."""
        self._sources[source.get_identifier()] = source
        L.info(f"Registered data source: {source.get_identifier()}")
    
    def get_source(self, identifier: str) -> Optional[BaseDataSource]:
        """Get a data source by identifier."""
        return self._sources.get(identifier)
    
    def list_sources(self) -> List[str]:
        """List all registered source identifiers."""
        return list(self._sources.keys())
    
    def get_enabled_sources(self) -> List[BaseDataSource]:
        """Get all enabled data sources."""
        return [source for source in self._sources.values() if source.config.enabled]

# Global registry instance
registry = DataSourceRegistry()
