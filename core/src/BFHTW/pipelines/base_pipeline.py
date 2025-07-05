"""
Base pipeline framework for multi-source data processing with robust validation.

Provides abstract base classes and common patterns for creating data processing
pipelines that are extensible, testable, and source-agnostic.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type, Generic, TypeVar
from pydantic import BaseModel, ValidationError
from dataclasses import dataclass
from enum import Enum
import time
from datetime import datetime
from uuid import uuid4

from BFHTW.utils.logs import get_logger
from BFHTW.utils.crud.crud import CRUD

L = get_logger()

# Type variables for generic pipeline components
SourceDataT = TypeVar('SourceDataT')
ProcessedDataT = TypeVar('ProcessedDataT', bound=BaseModel)

class PipelineStatus(Enum):
    """Pipeline execution status values."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PipelineResult:
    """Standard pipeline execution result."""
    pipeline_id: str
    status: PipelineStatus
    processed_count: int
    failed_count: int
    execution_time: float
    errors: List[str]
    metadata: Dict[str, Any]

@dataclass
class ValidationResult:
    """Data validation result."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    score: Optional[float] = None

class DataSource(ABC):
    """Abstract base class for data sources."""
    
    @abstractmethod
    def get_identifier(self) -> str:
        """Return unique identifier for this data source."""
        pass
    
    @abstractmethod
    def fetch_metadata(self) -> List[Dict[str, Any]]:
        """Fetch metadata from the source."""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate connection to data source."""
        pass

class DataValidator(ABC):
    """Abstract base class for data validators."""
    
    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Validate data and return validation result."""
        pass

class BasePipeline(ABC, Generic[SourceDataT, ProcessedDataT]):
    """
    Base class for all data processing pipelines.
    
    Provides common functionality for:
    - Data source management
    - Validation framework
    - Error handling and logging
    - Progress tracking
    - Transaction management
    """
    
    def __init__(
        self,
        name: str,
        source: DataSource,
        validators: Optional[List[DataValidator]] = None,
        batch_size: int = 100,
        max_retries: int = 3
    ):
        self.name = name
        self.source = source
        self.validators = validators or []
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.pipeline_id = str(uuid4())
        
    def run(self) -> PipelineResult:
        """Execute the complete pipeline with error handling and logging."""
        start_time = time.time()
        processed_count = 0
        failed_count = 0
        errors = []
        
        L.info(f"Starting pipeline {self.name} (ID: {self.pipeline_id})")
        
        try:
            # Pre-flight validation
            if not self.source.validate_connection():
                raise ConnectionError(f"Cannot connect to data source: {self.source.get_identifier()}")
            
            # Get data from source
            source_data = self.source.fetch_metadata()
            L.info(f"Retrieved {len(source_data)} items from {self.source.get_identifier()}")
            
            # Process in batches
            for batch_start in range(0, len(source_data), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(source_data))
                batch = source_data[batch_start:batch_end]
                
                batch_result = self._process_batch(batch)
                processed_count += batch_result.processed_count
                failed_count += batch_result.failed_count
                errors.extend(batch_result.errors)
                
                L.info(f"Processed batch {batch_start//self.batch_size + 1}: "
                      f"{batch_result.processed_count} success, {batch_result.failed_count} failed")
            
            status = PipelineStatus.SUCCESS if failed_count == 0 else PipelineStatus.FAILED
            
        except Exception as e:
            L.error(f"Pipeline {self.name} failed with error: {str(e)}")
            errors.append(str(e))
            status = PipelineStatus.FAILED
        
        execution_time = time.time() - start_time
        
        result = PipelineResult(
            pipeline_id=self.pipeline_id,
            status=status,
            processed_count=processed_count,
            failed_count=failed_count,
            execution_time=execution_time,
            errors=errors,
            metadata={
                "source": self.source.get_identifier(),
                "batch_size": self.batch_size,
                "total_items": len(source_data) if 'source_data' in locals() else 0
            }
        )
        
        self._log_result(result)
        return result
    
    def _process_batch(self, batch: List[SourceDataT]) -> PipelineResult:
        """Process a batch of items with validation and error handling."""
        processed_count = 0
        failed_count = 0
        errors = []
        
        for item in batch:
            try:
                # Validate input data
                validation_result = self._validate_item(item)
                if not validation_result.is_valid:
                    errors.extend(validation_result.errors)
                    failed_count += 1
                    continue
                
                # Process item
                processed_item = self.process_item(item)
                
                # Validate output
                if processed_item:
                    self.store_item(processed_item)
                    processed_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Processing returned None for item: {item}")
                    
            except ValidationError as e:
                errors.append(f"Validation error: {str(e)}")
                failed_count += 1
            except Exception as e:
                errors.append(f"Processing error: {str(e)}")
                failed_count += 1
        
        return PipelineResult(
            pipeline_id=self.pipeline_id,
            status=PipelineStatus.SUCCESS if failed_count == 0 else PipelineStatus.FAILED,
            processed_count=processed_count,
            failed_count=failed_count,
            execution_time=0,  # Individual batch time not tracked
            errors=errors,
            metadata={}
        )
    
    def _validate_item(self, item: SourceDataT) -> ValidationResult:
        """Run all validators on an item."""
        all_errors = []
        all_warnings = []
        
        for validator in self.validators:
            result = validator.validate(item)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )
    
    def _log_result(self, result: PipelineResult):
        """Log pipeline execution results."""
        if result.status == PipelineStatus.SUCCESS:
            L.info(f"Pipeline {self.name} completed successfully: "
                  f"{result.processed_count} processed in {result.execution_time:.2f}s")
        else:
            L.error(f"Pipeline {self.name} failed: "
                   f"{result.processed_count} processed, {result.failed_count} failed")
            for error in result.errors[:5]:  # Log first 5 errors
                L.error(f"Error: {error}")
    
    @abstractmethod
    def process_item(self, item: SourceDataT) -> Optional[ProcessedDataT]:
        """Process a single item from source data to target model."""
        pass
    
    @abstractmethod
    def store_item(self, item: ProcessedDataT) -> bool:
        """Store processed item in database/storage."""
        pass

class DatabaseValidator(DataValidator):
    """Validator for database schema compliance."""
    
    def __init__(self, model: Type[BaseModel]):
        self.model = model
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate data against Pydantic model."""
        try:
            self.model(**data) if isinstance(data, dict) else self.model.model_validate(data)
            return ValidationResult(is_valid=True, errors=[], warnings=[])
        except ValidationError as e:
            return ValidationResult(
                is_valid=False,
                errors=[str(error) for error in e.errors()],
                warnings=[]
            )

class ContentQualityValidator(DataValidator):
    """Validator for content quality metrics."""
    
    def __init__(self, min_text_length: int = 50, required_fields: Optional[List[str]] = None):
        self.min_text_length = min_text_length
        self.required_fields = required_fields or []
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate content quality."""
        errors = []
        warnings = []
        
        # Check required fields
        if isinstance(data, dict):
            for field in self.required_fields:
                if field not in data or not data[field]:
                    errors.append(f"Missing required field: {field}")
        
        # Check text length if text field exists
        text_content = ""
        if isinstance(data, dict) and 'text' in data:
            text_content = data['text']
        elif hasattr(data, 'text'):
            text_content = data.text
        
        if text_content and len(text_content.strip()) < self.min_text_length:
            warnings.append(f"Text content too short: {len(text_content)} < {self.min_text_length}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
