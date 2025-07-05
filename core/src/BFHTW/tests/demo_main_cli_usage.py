#!/usr/bin/env python3
"""
Practical example of running the main.py CLI with limited data for testing.

This script shows real CLI usage with controlled parameters for fast testing.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_cli_command(command, show_output=True):
    """Run a CLI command and capture output."""
    print(f"\n🔧 Running: python -m BFHTW.pipelines.main {' '.join(command)}")
    print("-" * 60)
    
    try:
        # Change to the project directory
        project_dir = Path(__file__).parent.parent
        
        result = subprocess.run(
            [sys.executable, "-m", "BFHTW.pipelines.main"] + command,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout for safety
        )
        
        if show_output:
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
        
        print(f"Exit code: {result.returncode}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out (60 seconds)")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def demonstrate_cli_usage():
    """Demonstrate various CLI commands with limited data."""
    print("🧪 MAIN.PY CLI DEMONSTRATION WITH LIMITED DATA")
    print("=" * 80)
    
    # Test configuration file path
    config_file = Path(__file__).parent / "test_pipeline_config.yaml"
    
    test_commands = [
        # Help command
        {
            "name": "Show Help",
            "command": ["--help"],
            "expected": True
        },
        
        # List available pipelines
        {
            "name": "List Pipelines",
            "command": ["list", "--config", str(config_file)],
            "expected": True
        },
        
        # Run PubMed metadata pipeline with very limited data
        {
            "name": "Run PubMed Metadata (Limited)",
            "command": [
                "run", "pubmed_metadata",
                "--max-articles", "3",    # Very small number
                "--batch-size", "2",      # Small batch
                "--lenient"               # Lenient validation for speed
            ],
            "expected": True  # May fail due to actual API calls, but should parse correctly
        },
        
        # Run document processing pipeline with AI disabled
        {
            "name": "Run Document Processing (No AI)",
            "command": [
                "run", "document_processing",
                "--max-articles", "2",    # Very small number
                "--batch-size", "1",      # Minimal batch
                "--no-ai",                # Disable AI for speed
                "--no-embeddings",        # Disable embeddings for speed
                "--lenient"               # Lenient validation
            ],
            "expected": True  # May fail due to dependencies, but should parse correctly
        },
        
        # Check pipeline status
        {
            "name": "Check Pipeline Status",
            "command": ["status"],
            "expected": True
        },
        
        # Check specific pipeline status
        {
            "name": "Check Specific Pipeline Status",
            "command": ["status", "--pipeline", "pubmed_metadata"],
            "expected": True
        },
        
        # Test invalid pipeline name (should fail gracefully)
        {
            "name": "Invalid Pipeline Name",
            "command": ["run", "invalid_pipeline"],
            "expected": False  # Should fail with exit code 1
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_commands, 1):
        print(f"\n📝 Test {i}/{len(test_commands)}: {test['name']}")
        
        start_time = time.time()
        success = run_cli_command(test['command'])
        duration = time.time() - start_time
        
        # Check if result matches expectation
        if success == test['expected']:
            status = "✅ PASS"
        else:
            status = "❌ FAIL" if test['expected'] else "✅ EXPECTED FAIL"
        
        results.append({
            'name': test['name'],
            'success': success,
            'expected': test['expected'],
            'duration': duration,
            'status': status
        })
        
        print(f"{status} (took {duration:.2f}s)")
    
    # Summary
    print(f"\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r['success'] == r['expected'])
    total = len(results)
    
    for result in results:
        print(f"{result['status']} {result['name']:<30} ({result['duration']:.2f}s)")
    
    print(f"\nOverall: {passed}/{total} tests behaved as expected")
    
    if passed == total:
        print("🎉 All CLI commands are working correctly!")
    else:
        print("⚠️  Some commands may need attention (but this is often expected)")
    
    print("\n💡 Tips for real usage:")
    print("  • Start with --max-articles 10 for initial testing")
    print("  • Use --no-ai --no-embeddings to speed up document processing")
    print("  • Use --lenient for faster validation during development")
    print("  • Check status regularly when running long pipelines")

if __name__ == "__main__":
    demonstrate_cli_usage()
