"""
Refactored PubMed Central pipeline using the new robust pipeline framework.

Demonstrates how to use the base pipeline architecture for reliable, 
validated data processing with comprehensive error handling.
"""

from typing import Optional, List
from pathlib import Path

from BFHTW.pipelines.base_pipeline import BasePipeline, PipelineResult
from BFHTW.pipelines.data_sources import PubMedCentralSource
from BFHTW.pipelines.validation import create_metadata_validators
from BFHTW.models.pubmed_pmc import PMCArticleMetadata
from BFHTW.utils.crud.crud import CRUD
from BFHTW.utils.logs import get_logger

L = get_logger()

class PubMedMetadataPipeline(BasePipeline[dict, PMCArticleMetadata]):
    """
    Pipeline for fetching and validating PubMed Central article metadata.
    
    Extends BasePipeline to provide PMC-specific processing logic while
    leveraging the framework's validation, error handling, and logging.
    """
    
    def __init__(
        self,
        search_terms_file: Optional[str] = None,
        max_articles: int = 1000,
        batch_size: int = 100,
        update_reference_files: bool = True,
        strict_validation: bool = True
    ):
        # Create PMC data source
        pmc_source = PubMedCentralSource(
            search_terms_file=search_terms_file,
            max_articles=max_articles,
            update_reference_files=update_reference_files
        )
        
        # Create validators for PMC article metadata
        required_fields = ['pmcid', 'ftp_path', 'source_db']
        foreign_keys = {} if not strict_validation else {}  # Add FK validation if needed
        
        validators = create_metadata_validators(
            model=PMCArticleMetadata,
            required_fields=required_fields,
            foreign_keys=foreign_keys
        )
        
        super().__init__(
            name="PubMed Metadata Pipeline",
            source=pmc_source,
            validators=validators,
            batch_size=batch_size,
            max_retries=3
        )
        
        self.strict_validation = strict_validation
    
    def process_item(self, item: dict) -> Optional[PMCArticleMetadata]:
        """
        Process a single metadata item from PMC source.
        
        Args:
            item: Raw metadata dict from PMC source
            
        Returns:
            PMCArticleMetadata instance or None if processing fails
        """
        try:
            # Create PMC article metadata model
            metadata = PMCArticleMetadata(**item)
            
            # Additional processing/enrichment could go here
            # For example:
            # - URL validation
            # - File size checking
            # - Metadata enhancement
            
            return metadata
            
        except Exception as e:
            L.error(f"Failed to process metadata item: {str(e)}")
            L.error(f"Item data: {item}")
            return None
    
    def store_item(self, item: PMCArticleMetadata) -> bool:
        """
        Store processed metadata in database.
        
        Args:
            item: Validated PMCArticleMetadata instance
            
        Returns:
            True if storage successful, False otherwise
        """
        try:
            # Check for existing record to avoid duplicates
            existing = CRUD.get(
                table='pubmed_fulltext_links',
                model=PMCArticleMetadata,
                id_field='pmcid',
                id_value=item.pmcid
            )
            
            if existing and self.strict_validation:
                L.warning(f"Duplicate PMCID found, skipping: {item.pmcid}")
                return False
            
            # Store in database
            result = CRUD.insert(
                table='pubmed_fulltext_links',
                model=PMCArticleMetadata,
                data=item
            )
            
            if result:
                L.debug(f"Stored metadata for PMCID: {item.pmcid}")
                return True
            else:
                L.error(f"Failed to store metadata for PMCID: {item.pmcid}")
                return False
                
        except Exception as e:
            L.error(f"Error storing metadata for PMCID {item.pmcid}: {str(e)}")
            return False

def run_pubmed_metadata_pipeline(
    search_terms_file: Optional[str] = None,
    max_articles: int = 1000,
    batch_size: int = 100,
    update_reference_files: bool = True,
    strict_validation: bool = True
) -> PipelineResult:
    """
    Execute the PubMed metadata pipeline.
    
    Args:
        search_terms_file: Path to search terms JSON file
        max_articles: Maximum number of articles to process
        batch_size: Number of items to process in each batch
        update_reference_files: Whether to update PMC reference files
        strict_validation: Whether to use strict validation rules
        
    Returns:
        PipelineResult with execution statistics and status
    """
    # Initialize and run pipeline
    pipeline = PubMedMetadataPipeline(
        search_terms_file=search_terms_file,
        max_articles=max_articles,
        batch_size=batch_size,
        update_reference_files=update_reference_files,
        strict_validation=strict_validation
    )
    
    # Create table if not exists
    CRUD.create_table_if_not_exists(
        table='pubmed_fulltext_links',
        model=PMCArticleMetadata,
        primary_key='pmcid'
    )
    
    # Execute pipeline
    result = pipeline.run()
    
    # Log summary
    if result.status.value == "success":
        L.info(f"PubMed metadata pipeline completed successfully:")
        L.info(f"  - Processed: {result.processed_count} articles")
        L.info(f"  - Execution time: {result.execution_time:.2f} seconds")
        L.info(f"  - Rate: {result.processed_count/result.execution_time:.1f} articles/second")
    else:
        L.error(f"PubMed metadata pipeline failed:")
        L.error(f"  - Processed: {result.processed_count} articles")
        L.error(f"  - Failed: {result.failed_count} articles")
        L.error(f"  - Errors: {len(result.errors)}")
    
    return result

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Run PubMed metadata pipeline")
    parser.add_argument("--search-terms", help="Path to search terms JSON file")
    parser.add_argument("--max-articles", type=int, default=1000, help="Maximum articles to process")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for processing")
    parser.add_argument("--no-update", action="store_true", help="Skip reference file updates")
    parser.add_argument("--lenient", action="store_true", help="Use lenient validation")
    
    args = parser.parse_args()
    
    result = run_pubmed_metadata_pipeline(
        search_terms_file=args.search_terms,
        max_articles=args.max_articles,
        batch_size=args.batch_size,
        update_reference_files=not args.no_update,
        strict_validation=not args.lenient
    )
    
    # Exit with appropriate code
    exit(0 if result.status.value == "success" else 1)
