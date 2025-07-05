# Validation Framework Test Instructions

This directory contains comprehensive tests for the BFHTW validation framework using real biomedical data.

## Files Created

1. **`test_validation_framework.py`** - Comprehensive test suite demonstrating all validation components
2. **`run_validation_demo.py`** - Simple runner script to execute the demonstration

## Test Features

The test suite demonstrates:

### **Schema Validation**
- Tests Pydantic model validation with valid/invalid data
- Shows how validation errors and warnings are handled

### **Biomedical Content Validation**
- Uses BioBERT vocabulary for intelligent biomedical term detection
- Tests with high/low biomedical content scores
- Extracts and validates real PDF content from: `/home/steven/BFHTW/core/src/BFHTW/sources/pubmed_pmc/temp/extract_PMC17774/PMC17774/ar-1-1-063.pdf`

### **Metadata Completeness**
- Validates required and recommended fields
- Tests field pattern matching (e.g., DOI format validation)

### **Composite Validation**
- Combines multiple validators into comprehensive validation pipelines
- Shows how validation results are aggregated

### **Factory Functions**
- Demonstrates pre-configured validator combinations for common use cases

### **Real-World Pipeline Simulation**
- Processes multiple documents through a complete validation pipeline
- Shows typical biomedical data processing workflow

## How to Run

### Option 1: Direct Execution
```bash
cd /home/steven/BFHTW/core/src/BFHTW
python run_validation_demo.py
```

### Option 2: Using pytest
```bash
cd /home/steven/BFHTW/core/src/BFHTW
python -m pytest tests/test_validation_framework.py -v -s
```

### Option 3: Individual Test Methods
```python
from tests.test_validation_framework import TestValidationFramework

test = TestValidationFramework()
test.setup_method()
test.test_biomedical_content_validator_with_pdf()
```

## Expected Output

The test will show you:

1. **BioBERT Vocabulary Loading**: How many biomedical terms are loaded from the BioBERT model
2. **PDF Text Extraction**: Content extracted from the actual PDF file
3. **Validation Scores**: Biomedical relevance scores for different types of content
4. **Error Detection**: How the system catches validation failures
5. **Warning Generation**: Non-critical issues like low biomedical content
6. **Pipeline Processing**: Complete document processing workflow

## Sample Output Preview

```
BIOMEDICAL DATA VALIDATION FRAMEWORK DEMONSTRATION
================================================================================

============================================================
Testing SchemaValidator - SUCCESS CASE
============================================================
Validation Result: True
Errors: []
Warnings: []
Schema validation passed for valid document

============================================================
Testing BiomedicalContentValidator - HIGH BIOMEDICAL SCORE
============================================================
Validation Result: True
Biomedical Score: 0.0847
Errors: []
Warnings: []
Biomedical validation passed with score: 0.0847

============================================================
Testing BiomedicalContentValidator - PDF CONTENT
============================================================
PDF Text Length: 15847 characters
Validation Result: True
Biomedical Score: 0.0234
Errors: []
Warnings: []
First 200 chars of PDF: Arthritis Research & Therapy    Vol 1 No 1    Lorenz...
PDF content validation completed with score: 0.0234
```

## Understanding the Results

- **Validation Result**: `True` means the document passes validation
- **Biomedical Score**: Higher scores (>0.05) indicate more biomedical content
- **Errors**: Critical validation failures that prevent processing
- **Warnings**: Non-critical issues that may affect quality

## Dependencies

Make sure these packages are installed:
- `transformers` (for BioBERT vocabulary)
- `pymupdf` (for PDF text extraction)
- `pydantic` (for schema validation)

All dependencies are included in `requirements/base.txt`.
