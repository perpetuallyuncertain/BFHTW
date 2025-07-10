"""
Data sources package for BFHTW pipelines.

This package provides unified data source implementations that integrate
with the pipeline framework.
"""

from .base_source import BaseDataSource, DataSourceConfig, SearchResult, DownloadInfo
from .registry import get_registry, register_source, get_source, list_sources

__all__ = [
    'BaseDataSource',
    'DataSourceConfig', 
    'SearchResult',
    'DownloadInfo',
    'get_registry',
    'register_source',
    'get_source',
    'list_sources'
]
