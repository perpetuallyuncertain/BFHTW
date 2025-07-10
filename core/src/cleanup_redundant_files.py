#!/usr/bin/env python3
"""
Cleanup script to remove redundant files after pipeline refactoring.

This script safely removes files that are no longer needed after the
unified pipeline architecture implementation.
"""

import os
import shutil
from pathlib import Path

def main():
    """Remove redundant files."""
    base_dir = Path(__file__).parent
    
    # Files to remove
    files_to_remove = [
        # Old pipeline files
        "BFHTW/pipelines/data_sources.py",
        "BFHTW/pipelines/pubmed_metadata_pipeline.py",
        "BFHTW/pipelines/pubmed_pmc/pubmed_fetch_metadata.py",
        "BFHTW/pipelines/pubmed_pmc/pubmed_download_and_parse.py",
        
        # Duplicate test file
        "test_architecture.py",
    ]
    
    # Cache directories to remove
    cache_dirs_to_remove = [
        "BFHTW/pipelines/__pycache__",
        "BFHTW/pipelines/pubmed_pmc/__pycache__",
        "BFHTW/sources/pubmed_pmc/__pycache__",
        "BFHTW/sources/pubmed_pmc/fetch/__pycache__",
    ]
    
    print("🧹 Cleaning up redundant files...")
    
    # Remove files
    for file_path in files_to_remove:
        full_path = base_dir / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
        else:
            print(f"⏭️ Already removed: {file_path}")
    
    # Remove cache directories
    for cache_dir in cache_dirs_to_remove:
        full_path = base_dir / cache_dir
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"✅ Removed cache: {cache_dir}")
            except Exception as e:
                print(f"❌ Failed to remove cache {cache_dir}: {e}")
        else:
            print(f"⏭️ Cache already clean: {cache_dir}")
    
    print("\n🎉 Cleanup complete!")
    print("\nRemaining files are still in use:")
    print("- sources/pubmed_pmc/pmc_api_client.py (used by new PMC source)")
    print("- sources/pubmed_pmc/merge_article_paths_with_pmids.py (deprecated, used by tests)")
    print("- sources/pubmed_pmc/fetch/ (used by new PMC source)")
    print("\nThese can be removed later once fully migrated.")

if __name__ == "__main__":
    main()
