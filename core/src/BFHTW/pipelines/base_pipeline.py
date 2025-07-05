"""
Core pipeline framework providing abstract base classes and utilities.

Provides the foundational architecture for robust, validated, and extensible 
biomedical data processing pipelines.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Dict, Any, Optional, Iterator, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
import time

from BFHTW.utils.logs import get_logger

L = get_logger()

# Type variables for generic pipeline implementation
InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')

class PipelineStatus(Enum):
    """Pipeline execution status."""
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning."""
        self.warnings.append(warning)

@dataclass 
class PipelineResult:
    """Result of pipeline execution."""
    status: PipelineStatus
    processed_count: int = 0
    failed_count: int = 0
    execution_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataValidator(ABC):
    """Abstract base class for data validators."""
    
    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Validate data and return validation result."""
        pass

class DataSource(ABC):
    """Abstract base class for data sources."""
    
    @abstractmethod
    def get_identifier(self) -> str:
        """Return unique identifier for this data source."""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate connection to data source."""
        pass
    
    @abstractmethod
    def fetch_metadata(self) -> List[Dict[str, Any]]:
        """Fetch metadata from data source."""
        pass

class BasePipeline(Generic[InputType, OutputType], ABC):
    """
    Abstract base class for all processing pipelines.
    
    Provides comprehensive pipeline lifecycle management including:
    - Standardized execution flow
    - Batch processing with progress tracking
    - Error handling and recovery
    - Validation integration
    - Result tracking and metrics
    """
    
    def __init__(
        self,
        name: str,
        source: DataSource,
        validators: List[DataValidator],
        batch_size: int = 100,
        max_retries: int = 3
    ):
        self.name = name
        self.source = source
        self.validators = validators
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.pipeline_id = str(uuid.uuid4())
        
    @abstractmethod
    def process_item(self, item: InputType) -> Optional[OutputType]:
        """Process a single item."""
        pass
    
    @abstractmethod
    def store_item(self, item: OutputType) -> bool:
        """Store processed item."""
        pass
    
    def validate_item(self, item: Any) -> ValidationResult:
        """Validate item using configured validators."""
        result = ValidationResult(is_valid=True)
        
        for validator in self.validators:
            validation = validator.validate(item)
            if not validation.is_valid:
                result.is_valid = False
                result.errors.extend(validation.errors)
            result.warnings.extend(validation.warnings)
        
        return result
    
    def run(self) -> PipelineResult:
        """Execute the complete pipeline."""
        start_time = time.time()
        result = PipelineResult(status=PipelineStatus.RUNNING)
        
        L.info(f"Starting pipeline: {self.name} (ID: {self.pipeline_id})")
        
        try:
            # Validate data source connection
            if not self.source.validate_connection():
                raise ConnectionError(f"Cannot connect to data source: {self.source.get_identifier()}")
            
            # Fetch data from source
            raw_data = self.source.fetch_metadata()
            L.info(f"Fetched {len(raw_data)} items from {self.source.get_identifier()}")
            
            # Process data in batches
            total_items = len(raw_data)
            processed = 0
            failed = 0
            
            for i in range(0, total_items, self.batch_size):
                batch = raw_data[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                total_batches = (total_items + self.batch_size - 1) // self.batch_size
                
                L.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")
                
                for item in batch:
                    try:
                        # Validate input
                        validation = self.validate_item(item)
                        if not validation.is_valid:
                            L.warning(f"Validation failed for item: {validation.errors}")
                            result.warnings.extend(validation.errors)
                            failed += 1
                            continue
                        
                        # Process item
                        processed_item = self.process_item(item)
                        if processed_item is None:
                            failed += 1
                            continue
                        
                        # Store result
                        if self.store_item(processed_item):
                            processed += 1
                        else:
                            failed += 1
                            
                    except Exception as e:
                        error_msg = f"Error processing item: {str(e)}"
                        L.error(error_msg)
                        result.errors.append(error_msg)
                        failed += 1
            
            # Set final status
            if failed == 0:
                result.status = PipelineStatus.SUCCESS
            elif processed > 0:
                result.status = PipelineStatus.SUCCESS  # Partial success
                result.warnings.append(f"Pipeline completed with {failed} failures")
            else:
                result.status = PipelineStatus.FAILED
            
            result.processed_count = processed
            result.failed_count = failed
            result.execution_time = time.time() - start_time
            
            L.info(f"Pipeline completed: {result.status.value}")
            L.info(f"  Processed: {processed}")
            L.info(f"  Failed: {failed}")
            L.info(f"  Execution time: {result.execution_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            L.error(error_msg)
            result.status = PipelineStatus.FAILED
            result.errors.append(error_msg)
            result.execution_time = time.time() - start_time
            return result
