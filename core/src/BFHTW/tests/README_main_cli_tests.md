# Main CLI Testing Documentation

This directory contains comprehensive tests for the `main.py` pipeline CLI interface with controlled datasets and limited processing for efficient testing.

## Files Created

### 1. **`test_main_cli.py`** - Comprehensive Test Suite
- **Mock-based testing** of all CLI commands
- **Controlled datasets** with minimal processing limits
- **Integration tests** with dummy data
- **Error handling validation**

### 2. **`demo_main_cli_usage.py`** - Practical CLI Demo
- **Real CLI execution** with subprocess calls
- **Limited data processing** (2-10 articles max)
- **Timeout protection** (60 seconds max per command)
- **Performance measurement** and result summary

### 3. **`test_pipeline_config.yaml`** - Test Configuration
- **Minimal processing settings** for speed
- **Disabled AI/embeddings** for faster testing
- **Small batch sizes** (1-5 items)
- **Lenient validation** for development

### 4. **`run_main_cli_demo.py`** - Simple Test Runner
- **Easy execution** without pytest
- **Mock-based demonstration**
- **Error handling** for missing dependencies

## Quick Start

### Option 1: Mock-Based Testing (Fastest)
```bash
cd /home/steven/BFHTW/core/src/BFHTW/tests
python run_main_cli_demo.py
```

### Option 2: Real CLI Testing (More Realistic)
```bash
cd /home/steven/BFHTW/core/src/BFHTW/tests
python demo_main_cli_usage.py
```

### Option 3: Pytest Execution
```bash
cd /home/steven/BFHTW/core/src/BFHTW
python -m pytest tests/test_main_cli.py -v -s
```

## Test Features

### **Limited Data Processing**
- **Max Articles**: 2-10 (vs normal 1000+)
- **Batch Size**: 1-5 (vs normal 100+)
- **AI Processing**: Disabled for speed
- **Embeddings**: Disabled for speed
- **Validation**: Lenient mode

### **CLI Commands Tested**
1. **`run pubmed_metadata`** - PubMed article metadata extraction
2. **`run document_processing`** - Document parsing and processing
3. **`scheduler`** - Background pipeline scheduling
4. **`status`** - Pipeline status monitoring
5. **`list`** - Available pipeline listing

### **Test Scenarios**
- **Success Cases**: Valid commands with expected results
- **Failure Cases**: Invalid pipelines, missing parameters
- **Integration**: End-to-end pipeline execution
- **Performance**: Execution time measurement

## Sample Output

```bash
MAIN.PY CLI DEMONSTRATION WITH LIMITED DATA
================================================================================

Test 1/7: Show Help
Running: python -m BFHTW.pipelines.main --help
------------------------------------------------------------
STDOUT:
usage: main.py [-h] {run,scheduler,status,list} ...
...
PASS (took 0.23s)

Test 2/7: Run PubMed Metadata (Limited)
Running: python -m BFHTW.pipelines.main run pubmed_metadata --max-articles 3 --batch-size 2 --lenient
------------------------------------------------------------
{"message": "Running pipeline: pubmed_metadata", "level": "INFO"}
{"message": "Pipeline completed successfully", "level": "INFO"}
Processed: 3
Failed: 0
Execution time: 12.50s
PASS (took 12.75s)
```

## Configuration Details

### Test Pipeline Settings
```yaml
pipelines:
  test_pubmed_metadata:
    batch_size: 5        # vs normal 100
    max_articles: 10     # vs normal 1000+
    validation:
      strict: false      # Lenient for speed
  
  test_document_processing:
    batch_size: 3        # vs normal 50
    max_articles: 5      # vs normal unlimited
    ai_processing:
      enable_ai: false   # Disabled for speed
      enable_embeddings: false
```

### Safety Features
- **Timeout Protection**: 60 seconds max per command
- **Small Data Limits**: 1-10 articles maximum
- **Error Handling**: Graceful failure management
- **Resource Limits**: Minimal CPU/memory usage

## Usage Examples

### Test with Minimal Data
```bash
# Test PubMed pipeline with just 2 articles
python -m BFHTW.pipelines.main run pubmed_metadata --max-articles 2 --batch-size 1 --lenient

# Test document processing without AI
python -m BFHTW.pipelines.main run document_processing --max-articles 1 --no-ai --no-embeddings

# Check pipeline status
python -m BFHTW.pipelines.main status

# List available pipelines
python -m BFHTW.pipelines.main list --config tests/test_pipeline_config.yaml
```

### Test Scheduler (Background Mode)
```bash
# Start scheduler with test config
python -m BFHTW.pipelines.main scheduler --config tests/test_pipeline_config.yaml
```

## Performance Expectations

| Command | Expected Time | Data Processed |
|---------|---------------|----------------|
| Help | < 1 second | N/A |
| List | < 2 seconds | Configuration only |
| Status | < 3 seconds | Database queries |
| PubMed (2 articles) | 5-15 seconds | Minimal API calls |
| Document Processing (1 doc) | 3-10 seconds | No AI processing |

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Timeout Errors**: Reduce max_articles further (try 1)
3. **API Limits**: PubMed may rate-limit requests
4. **Database Errors**: Check database connectivity

### Debug Mode
```bash
# Add verbose logging
export PYTHONPATH=/home/steven/BFHTW/core/src
python -m BFHTW.pipelines.main run pubmed_metadata --max-articles 1 --batch-size 1 --lenient
```

## Integration with CI/CD

These tests are designed to be:
- **Fast** (< 60 seconds total)
- **Reliable** (mocked dependencies)
- **Isolated** (no external API dependencies for core tests)
- **Comprehensive** (all CLI commands covered)

Perfect for automated testing in CI/CD pipelines!
