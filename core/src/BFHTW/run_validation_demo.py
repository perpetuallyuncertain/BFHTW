#!/usr/bin/env python3
"""
Simple runner script to demonstrate the validation framework.
Run this to see how the validation system works with real data.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_validation_framework import run_comprehensive_validation_demo

if __name__ == "__main__":
    print("Starting Validation Framework Demonstration...")
    print("This will show you how all the validators work with real biomedical data.")
    print()
    
    try:
        run_comprehensive_validation_demo()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you have all required packages installed:")
        print("  pip install transformers pymupdf")
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
