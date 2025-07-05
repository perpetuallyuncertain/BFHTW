"""
Pipeline configuration and management utilities.

Provides centralized configuration, scheduling, and monitoring for all pipelines.
"""

from typing import Dict, List, Any, Optional, Type, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import json
import yaml
from datetime import datetime, timedelta
import schedule
import time

from BFHTW.pipelines.base_pipeline import BasePipeline, PipelineResult, PipelineStatus
from BFHTW.utils.logs import get_logger

L = get_logger()

class ScheduleType(Enum):
    """Pipeline schedule types."""
    MANUAL = "manual"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    CRON = "cron"

@dataclass
class PipelineConfig:
    """Configuration for a single pipeline."""
    name: str
    pipeline_class: str
    enabled: bool = True
    schedule_type: ScheduleType = ScheduleType.MANUAL
    schedule_params: Dict[str, Any] = None
    max_runtime_minutes: int = 60
    retry_attempts: int = 3
    parameters: Dict[str, Any] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.schedule_params is None:
            self.schedule_params = {}
        if self.parameters is None:
            self.parameters = {}
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class PipelineExecution:
    """Record of pipeline execution."""
    pipeline_name: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: PipelineStatus = PipelineStatus.RUNNING
    result: Optional[PipelineResult] = None
    error_message: Optional[str] = None

class PipelineManager:
    """
    Central manager for pipeline configuration, scheduling, and execution.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else Path("pipeline_config.yaml")
        self.pipelines: Dict[str, PipelineConfig] = {}
        self.executions: List[PipelineExecution] = []
        self.running_pipelines: Dict[str, PipelineExecution] = {}
        
        # Load configuration
        self.load_config()
        
        # Setup scheduling
        self.setup_schedules()
    
    def load_config(self):
        """Load pipeline configuration from file."""
        if not self.config_file.exists():
            L.warning(f"Pipeline config file not found: {self.config_file}")
            self.create_default_config()
            return
        
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.suffix.lower() == '.yaml':
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            for name, config in config_data.get('pipelines', {}).items():
                self.pipelines[name] = PipelineConfig(
                    name=name,
                    **config
                )
            
            L.info(f"Loaded configuration for {len(self.pipelines)} pipelines")
            
        except Exception as e:
            L.error(f"Failed to load pipeline config: {str(e)}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default pipeline configuration."""
        default_config = {
            'pipelines': {
                'pubmed_metadata': {
                    'pipeline_class': 'BFHTW.pipelines.pubmed_metadata_pipeline.PubMedMetadataPipeline',
                    'enabled': True,
                    'schedule_type': 'daily',
                    'schedule_params': {'time': '02:00'},
                    'max_runtime_minutes': 30,
                    'parameters': {
                        'max_articles': 1000,
                        'batch_size': 100,
                        'update_reference_files': True
                    }
                },
                'document_processing': {
                    'pipeline_class': 'BFHTW.pipelines.document_processing_pipeline.DocumentProcessingPipeline',
                    'enabled': True,
                    'schedule_type': 'hourly',
                    'schedule_params': {},
                    'max_runtime_minutes': 120,
                    'parameters': {
                        'batch_size': 5,
                        'enable_ai_processing': True,
                        'enable_embeddings': True
                    },
                    'dependencies': ['pubmed_metadata']
                }
            }
        }
        
        # Save default config
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        # Load the default config
        for name, config in default_config['pipelines'].items():
            self.pipelines[name] = PipelineConfig(
                name=name,
                **config
            )
        
        L.info(f"Created default configuration with {len(self.pipelines)} pipelines")
    
    def setup_schedules(self):
        """Setup scheduled execution for configured pipelines."""
        for pipeline_name, config in self.pipelines.items():
            if not config.enabled or config.schedule_type == ScheduleType.MANUAL:
                continue
            
            try:
                if config.schedule_type == ScheduleType.HOURLY:
                    schedule.every().hour.do(self.run_pipeline, pipeline_name)
                    
                elif config.schedule_type == ScheduleType.DAILY:
                    time_str = config.schedule_params.get('time', '02:00')
                    schedule.every().day.at(time_str).do(self.run_pipeline, pipeline_name)
                    
                elif config.schedule_type == ScheduleType.WEEKLY:
                    day = config.schedule_params.get('day', 'monday')
                    time_str = config.schedule_params.get('time', '02:00')
                    getattr(schedule.every(), day).at(time_str).do(self.run_pipeline, pipeline_name)
                
                L.info(f"Scheduled pipeline '{pipeline_name}' for {config.schedule_type.value} execution")
                
            except Exception as e:
                L.error(f"Failed to schedule pipeline '{pipeline_name}': {str(e)}")
    
    def run_pipeline(self, pipeline_name: str, **override_params) -> Optional[PipelineResult]:
        """
        Execute a specific pipeline.
        
        Args:
            pipeline_name: Name of pipeline to run
            **override_params: Parameters to override configuration
            
        Returns:
            PipelineResult or None if failed to start
        """
        if pipeline_name not in self.pipelines:
            L.error(f"Unknown pipeline: {pipeline_name}")
            return None
        
        config = self.pipelines[pipeline_name]
        
        if not config.enabled:
            L.warning(f"Pipeline '{pipeline_name}' is disabled")
            return None
        
        # Check if already running
        if pipeline_name in self.running_pipelines:
            L.warning(f"Pipeline '{pipeline_name}' is already running")
            return None
        
        # Check dependencies
        if not self._check_dependencies(config):
            L.error(f"Dependencies not satisfied for pipeline '{pipeline_name}'")
            return None
        
        execution_id = f"{pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        execution = PipelineExecution(
            pipeline_name=pipeline_name,
            execution_id=execution_id,
            start_time=datetime.now()
        )
        
        self.running_pipelines[pipeline_name] = execution
        self.executions.append(execution)
        
        L.info(f"Starting pipeline '{pipeline_name}' (execution: {execution_id})")
        
        try:
            # Import and instantiate pipeline class
            pipeline_instance = self._create_pipeline_instance(config, override_params)
            
            # Run pipeline with timeout
            result = self._run_with_timeout(pipeline_instance, config.max_runtime_minutes)
            
            # Update execution record
            execution.end_time = datetime.now()
            execution.status = result.status if result else PipelineStatus.FAILED
            execution.result = result
            
            # Log result
            if result and result.status == PipelineStatus.SUCCESS:
                L.info(f"Pipeline '{pipeline_name}' completed successfully")
            else:
                L.error(f"Pipeline '{pipeline_name}' failed")
            
            return result
            
        except Exception as e:
            error_msg = f"Pipeline '{pipeline_name}' failed with error: {str(e)}"
            L.error(error_msg)
            
            execution.end_time = datetime.now()
            execution.status = PipelineStatus.FAILED
            execution.error_message = error_msg
            
            return None
            
        finally:
            # Remove from running pipelines
            if pipeline_name in self.running_pipelines:
                del self.running_pipelines[pipeline_name]
    
    def _check_dependencies(self, config: PipelineConfig) -> bool:
        """Check if pipeline dependencies are satisfied."""
        if not config.dependencies:
            return True
        
        for dep_name in config.dependencies:
            # Check if dependency ran successfully recently
            recent_executions = [
                ex for ex in self.executions
                if ex.pipeline_name == dep_name
                and ex.status == PipelineStatus.SUCCESS
                and ex.end_time
                and ex.end_time > datetime.now() - timedelta(hours=24)
            ]
            
            if not recent_executions:
                L.warning(f"Dependency '{dep_name}' has no recent successful executions")
                return False
        
        return True
    
    def _create_pipeline_instance(self, config: PipelineConfig, override_params: Dict) -> BasePipeline:
        """Create pipeline instance from configuration."""
        # Import pipeline class
        module_path, class_name = config.pipeline_class.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        pipeline_class = getattr(module, class_name)
        
        # Merge parameters
        params = {**config.parameters, **override_params}
        
        # Create instance
        return pipeline_class(**params)
    
    def _run_with_timeout(self, pipeline: BasePipeline, timeout_minutes: int) -> Optional[PipelineResult]:
        """Run pipeline with timeout."""
        # TODO: Implement proper timeout handling
        # For now, just run the pipeline normally
        return pipeline.run()
    
    def get_pipeline_status(self, pipeline_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of pipelines."""
        if pipeline_name:
            if pipeline_name in self.running_pipelines:
                return {
                    "status": "running",
                    "execution": asdict(self.running_pipelines[pipeline_name])
                }
            else:
                recent = self._get_recent_execution(pipeline_name)
                return {
                    "status": "idle",
                    "last_execution": asdict(recent) if recent else None
                }
        else:
            return {
                "running": {name: asdict(ex) for name, ex in self.running_pipelines.items()},
                "recent_executions": [asdict(ex) for ex in self.executions[-10:]]
            }
    
    def _get_recent_execution(self, pipeline_name: str) -> Optional[PipelineExecution]:
        """Get most recent execution for a pipeline."""
        executions = [ex for ex in self.executions if ex.pipeline_name == pipeline_name]
        return max(executions, key=lambda x: x.start_time) if executions else None
    
    def start_scheduler(self):
        """Start the pipeline scheduler."""
        L.info("Starting pipeline scheduler...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                L.info("Pipeline scheduler stopped")
                break
            except Exception as e:
                L.error(f"Scheduler error: {str(e)}")
                time.sleep(60)

# Convenience functions
def create_pipeline_manager(config_file: Optional[str] = None) -> PipelineManager:
    """Create and configure pipeline manager."""
    return PipelineManager(config_file)

def run_pipeline_by_name(pipeline_name: str, manager: Optional[PipelineManager] = None) -> Optional[PipelineResult]:
    """Run a specific pipeline by name."""
    if manager is None:
        manager = create_pipeline_manager()
    
    return manager.run_pipeline(pipeline_name)
