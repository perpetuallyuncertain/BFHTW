"""
Main entry point for BFHTW pipeline execution.

Provides a unified command-line interface for running all pipelines
with comprehensive configuration and monitoring.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from BFHTW.pipelines.pipeline_manager import PipelineManager, create_pipeline_manager
from BFHTW.pipelines.pubmed_pmc.pubmed_metadata_pipeline import run_pubmed_metadata_pipeline
from BFHTW.pipelines.document_processing_pipeline import run_document_processing_pipeline
from BFHTW.utils.logs import get_logger

L = get_logger()

def main():
    """Main entry point for pipeline execution."""
    parser = argparse.ArgumentParser(
        description="BFHTW Pipeline Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run specific pipeline
  python -m BFHTW.pipelines.main run pubmed_metadata --max-articles 100
  
  # Start scheduler
  python -m BFHTW.pipelines.main scheduler --config pipeline_config.yaml
  
  # Check pipeline status
  python -m BFHTW.pipelines.main status --pipeline document_processing
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a specific pipeline')
    run_parser.add_argument('pipeline', choices=['pubmed_metadata', 'document_processing'],
                           help='Pipeline to run')
    run_parser.add_argument('--max-articles', type=int, help='Maximum articles to process')
    run_parser.add_argument('--batch-size', type=int, default=100, help='Batch size')
    run_parser.add_argument('--no-ai', action='store_true', help='Disable AI processing')
    run_parser.add_argument('--no-embeddings', action='store_true', help='Disable embeddings')
    run_parser.add_argument('--lenient', action='store_true', help='Use lenient validation')
    
    # Scheduler command
    scheduler_parser = subparsers.add_parser('scheduler', help='Start pipeline scheduler')
    scheduler_parser.add_argument('--config', help='Pipeline configuration file')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check pipeline status')
    status_parser.add_argument('--pipeline', help='Specific pipeline to check')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available pipelines')
    list_parser.add_argument('--config', help='Pipeline configuration file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'run':
            return run_pipeline_command(args)
        elif args.command == 'scheduler':
            return run_scheduler_command(args)
        elif args.command == 'status':
            return run_status_command(args)
        elif args.command == 'list':
            return run_list_command(args)
        else:
            L.error(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        L.info("Operation cancelled by user")
        return 0
    except Exception as e:
        L.error(f"Command failed: {str(e)}")
        return 1

def run_pipeline_command(args) -> int:
    """Execute a specific pipeline."""
    L.info(f"Running pipeline: {args.pipeline}")
    
    if args.pipeline == 'pubmed_metadata':
        result = run_pubmed_metadata_pipeline(
            max_articles=args.max_articles or 1000,
            batch_size=args.batch_size,
            strict_validation=not args.lenient
        )
    elif args.pipeline == 'document_processing':
        result = run_document_processing_pipeline(
            batch_size=args.batch_size,
            max_articles=args.max_articles,
            enable_ai=not args.no_ai,
            enable_embeddings=not args.no_embeddings
        )
    else:
        L.error(f"Unknown pipeline: {args.pipeline}")
        return 1
    
    if result and result.status.value == "success":
        L.info(f"Pipeline completed successfully")
        print(f"Processed: {result.processed_count}")
        print(f"Failed: {result.failed_count}")
        print(f"Execution time: {result.execution_time:.2f}s")
        return 0
    else:
        L.error(f"Pipeline failed")
        if result:
            print(f"Processed: {result.processed_count}")
            print(f"Failed: {result.failed_count}")
            print(f"Errors: {len(result.errors)}")
        return 1

def run_scheduler_command(args) -> int:
    """Start the pipeline scheduler."""
    L.info("Starting pipeline scheduler...")
    
    try:
        manager = create_pipeline_manager(args.config)
        manager.start_scheduler()  # Runs indefinitely
        return 0
    except Exception as e:
        L.error(f"Scheduler failed: {str(e)}")
        return 1

def run_status_command(args) -> int:
    """Check pipeline status."""
    try:
        manager = create_pipeline_manager()
        status = manager.get_pipeline_status(args.pipeline)
        
        if args.pipeline:
            print(f"Pipeline: {args.pipeline}")
            print(f"Status: {status['status']}")
            if status.get('last_execution'):
                exec_info = status['last_execution']
                print(f"Last execution: {exec_info['start_time']}")
                print(f"Result: {exec_info['status']}")
        else:
            print("Running pipelines:")
            for name, execution in status['running'].items():
                print(f"  {name}: started {execution['start_time']}")
            
            print("\nRecent executions:")
            for execution in status['recent_executions'][-5:]:
                print(f"  {execution['pipeline_name']}: {execution['status']} "
                      f"({execution['start_time']})")
        
        return 0
        
    except Exception as e:
        L.error(f"Status check failed: {str(e)}")
        return 1

def run_list_command(args) -> int:
    """List available pipelines."""
    try:
        manager = create_pipeline_manager(args.config)
        
        print("Available pipelines:")
        for name, config in manager.pipelines.items():
            status = "enabled" if config.enabled else "disabled"
            schedule = config.schedule_type.value
            print(f"  {name}: {status}, schedule: {schedule}")
        
        return 0
        
    except Exception as e:
        L.error(f"List command failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
