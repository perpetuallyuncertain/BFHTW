#!/usr/bin/env python3
"""
Simple runner script to test the main.py CLI interface.
This script demonstrates all CLI functionality with controlled, limited datasets.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_main_cli import run_comprehensive_main_cli_demo

if __name__ == "__main__":
    print("Starting Main CLI Testing Demonstration...")
    print("This will test all CLI commands with dummy data and limited processing.")
    print()
    
    try:
        run_comprehensive_main_cli_demo()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you have all required packages installed")
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
