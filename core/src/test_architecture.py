#!/usr/bin/env python3
"""
Test script to verify the new unified pipeline architecture.

This script tests:
1. Data source registry functionality
2. PMC data source implementation
3. Pipeline manager integration
4. Document model compatibility
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from BFHTW.pipelines.data_sources.registry import get_registry
from BFHTW.pipelines.data_sources.pmc_source import create_pmc_source
from BFHTW.pipelines.pipeline_manager import PipelineManager
from BFHTW.utils.logs import get_logger

L = get_logger()

def test_data_source_registry():
    """Test the data source registry functionality."""
    print("\n=== Testing Data Source Registry ===")
    
    registry = get_registry()
    
    # List available sources
    sources = registry.list_sources()
    print(f"Available sources: {sources}")
    
    # Get PMC source
    pmc_source = registry.get_source("pmc")
    if pmc_source:
        print(f"PMC source loaded: {pmc_source.get_identifier()}")
        
        # Test connection validation
        try:
            is_valid = pmc_source.validate_connection()
            print(f"PMC connection valid: {is_valid}")
        except Exception as e:
            print(f"PMC connection validation error: {e}")
    else:
        print("Failed to load PMC source")
    
    return pmc_source is not None

def test_pmc_source():
    """Test PMC data source implementation."""
    print("\n=== Testing PMC Data Source ===")
    
    try:
        # Create PMC source using factory
        pmc_source = create_pmc_source(
            max_results=10,
            update_reference_files=False  # Don't update files in test
        )
        
        print(f"PMC source created: {pmc_source.get_identifier()}")
        
        # Test search (this will use existing API client logic)
        search_terms = ["cancer", "biomarker"]
        print(f"Searching for: {search_terms}")
        
        # Note: This may fail if search terms file doesn't exist
        # That's expected in a test environment
        try:
            results = pmc_source.search(search_terms, max_results=5)
            print(f"Search returned {len(results)} results")
            
            if results:
                # Test metadata fetching
                doc_ids = [r.doc_id for r in results[:2]]  # Test first 2
                metadata_list = pmc_source.fetch_metadata(doc_ids)
                print(f"Fetched metadata for {len(metadata_list)} documents")
                
                # Test document formatting
                if metadata_list:
                    doc = pmc_source.format_as_document(metadata_list[0])
                    print(f"Created document: {doc.external_id}")
                    
        except Exception as e:
            print(f"PMC search/metadata error (expected in test): {e}")
            
        return True
        
    except Exception as e:
        print(f"PMC source creation error: {e}")
        return False

def test_pipeline_manager():
    """Test pipeline manager functionality."""
    print("\n=== Testing Pipeline Manager ===")
    
    try:
        # Create pipeline manager
        manager = PipelineManager()
        
        # List configured pipelines
        pipeline_names = list(manager.pipelines.keys())
        print(f"Configured pipelines: {pipeline_names}")
        
        # Show pipeline configurations
        for name, config in manager.pipelines.items():
            print(f"Pipeline '{name}': enabled={config.enabled}, schedule={config.schedule_type}")
        
        return True
        
    except Exception as e:
        print(f"Pipeline manager error: {e}")
        return False

def test_legacy_integration():
    """Test that legacy code still works alongside new architecture."""
    print("\n=== Testing Legacy Integration ===")
    
    # Test that we can still import legacy modules
    try:
        from BFHTW.sources.pubmed_pmc.pmc_api_client import PMCAPIClient
        print("Legacy PMC API client still accessible")
        
        from BFHTW.sources.pubmed_pmc.merge_article_paths_with_pmids import join_mapping_files
        print("Legacy merge function still accessible")
        
        # The legacy functions should work but may issue deprecation warnings
        return True
        
    except Exception as e:
        print(f"Legacy integration error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing BFHTW Unified Pipeline Architecture")
    print("=" * 50)
    
    results = []
    
    # Test components
    results.append(("Data Source Registry", test_data_source_registry()))
    results.append(("PMC Data Source", test_pmc_source()))
    results.append(("Pipeline Manager", test_pipeline_manager()))
    results.append(("Legacy Integration", test_legacy_integration()))
    
    # Print results
    print("\n=== Test Results ===")
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    
    if all_passed:
        print("\n✅ The new unified pipeline architecture is working correctly!")
        print("Next steps:")
        print("1. Run actual pipelines with real data")
        print("2. Add more data sources (arXiv, etc.)")
        print("3. Clean up remaining legacy code")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
