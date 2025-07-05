# Database Testing Suite

Comprehensive test suite for validating BFHTW's database operations, data models, and CRUD functionality. These tests ensure data integrity, performance, and reliability across all biomedical document processing workflows.

## Overview

The database testing suite provides thorough validation of:

- **CRUD Operations**: Create, Read, Update, Delete functionality for all models
- **Data Integrity**: Foreign key relationships and constraint validation
- **Performance Testing**: Bulk operations and query optimization
- **Error Handling**: Graceful handling of edge cases and failures
- **Migration Testing**: Schema evolution and backward compatibility

## Test Organization

```
tests/db/
├── test_create.py              # Document and entity creation tests
├── test_fetch.py               # Data retrieval and query tests  
├── test_get_unprocessed.py     # Processing queue management tests
├── test_bulk_operations.py     # Batch processing performance tests
├── test_data/                  # Test fixtures and sample data
│   ├── test_metadata.json     # Sample PDF metadata
│   ├── test_entities.json     # Sample biomedical entities
│   └── test_documents.json    # Sample document records
└── README.md                   # This file
```

## Core Test Categories

### Document Management Tests (`test_create.py`)
- **Document Creation**: Validate document model instantiation and storage
- **Metadata Handling**: Test PDF and NXML metadata processing
- **Foreign Key Integrity**: Ensure proper relationships between tables
- **Validation Rules**: Test Pydantic model validation and constraints

### Data Retrieval Tests (`test_fetch.py`)
- **Query Performance**: Validate query execution times and optimization
- **Filter Operations**: Test complex filtering and search operations
- **Join Operations**: Validate multi-table query performance
- **Result Validation**: Ensure returned data matches expected formats

### Processing Queue Tests (`test_get_unprocessed.py`)
- **Queue Management**: Test unprocessed document identification
- **Status Tracking**: Validate processing state transitions
- **Priority Handling**: Test article processing prioritization
## Test Examples

### Document Creation Testing
```python
def test_create_pdf_metadata():
    """Test PDF metadata creation and validation."""
    # Load test data
    with open('test_data/test_metadata.json') as f:
        test_data = json.load(f)
    
    # Create PDF metadata instance
    pdf_meta = PDFMetadata(**test_data)
    
    # Insert into database
    result = CRUD.insert(
        table='pdf_metadata',
        model=PDFMetadata,
        data=pdf_meta
    )
    
    # Validate insertion
    assert result.doc_id == pdf_meta.doc_id
    assert result.title == test_data['title']
```

### Bulk Operations Testing
```python
def test_bulk_insert_performance():
    """Test bulk insertion performance and data integrity."""
    # Generate test entities
    test_entities = [
        BiomedicalEntityBlock(
            block_id=f"block_{i}",
            doc_id="test_doc",
            medications=["cisplatin", "doxorubicin"],
            diseases=["hepatoblastoma"]
        )
        for i in range(1000)
    ]
    
    # Measure bulk insert performance
    start_time = time.time()
    CRUD.bulk_insert(
        table='bio_blocks',
        model=BiomedicalEntityBlock,
        data_list=test_entities
    )
    execution_time = time.time() - start_time
    
    # Validate performance and data integrity
    assert execution_time < 5.0  # Should complete within 5 seconds
    assert len(get_all_entities()) == 1000
```

### Query Performance Testing
```python
def test_complex_query_performance():
    """Test complex filtering and join operations."""
    # Test entity filtering by medication
    results = CRUD.get(
        table='bio_blocks',
        model=BiomedicalEntityBlock,
        id_field='medications',
        id_value='cisplatin'
    )
    
    # Validate results
    assert all('cisplatin' in entity.medications for entity in results)
    assert len(results) > 0
    
    # Test document-entity join performance
    joined_results = CRUD.get_documents_with_entities(
        entity_type='medications',
        entity_value='hepatoblastoma'
    )
    
    # Validate join results
    assert all(hasattr(result, 'document') for result in joined_results)
    assert all(hasattr(result, 'entities') for result in joined_results)
```

## Test Data Management

### Fixtures and Sample Data
```python
# test_data/test_metadata.json
{
    "doc_id": "test_doc_123",
    "title": "Hepatoblastoma Treatment Outcomes",
    "format": "pdf",
    "authors": ["Dr. Smith", "Dr. Johnson"],
    "journal": "Pediatric Oncology Journal",
    "publication_date": "2024-01-15",
    "doi": "10.1234/test.doi"
}

# test_data/test_entities.json
{
    "block_id": "test_block_123",
    "doc_id": "test_doc_123",
    "medications": ["cisplatin", "doxorubicin"],
    "diseases": ["hepatoblastoma", "liver_cancer"],
    "symptoms": ["abdominal_pain", "weight_loss"],
    "model": "biobert_v1.0",
    "embeddings": false
}
```

### Database Setup and Teardown
```python
@pytest.fixture(scope="function")
def test_database():
    """Create temporary test database."""
    # Setup test database
    test_db_path = "test_database.db"
    CRUD.initialize_database(test_db_path)
    
    yield test_db_path
    
    # Cleanup after test
    os.remove(test_db_path)

@pytest.fixture
def sample_documents():
    """Provide sample document data for testing."""
    return [
        Document(
            source_db="test_source",
            external_id=f"TEST_{i}",
            format="pdf",
            title=f"Test Document {i}"
        )
        for i in range(10)
    ]
```

## Performance Benchmarks

### Expected Performance Targets
- **Single Insert**: < 10ms per document
- **Bulk Insert (1000 records)**: < 5 seconds
- **Simple Query**: < 50ms
- **Complex Join Query**: < 200ms
- **Index Search**: < 20ms

### Performance Testing
```python
def test_database_performance():
    """Comprehensive database performance testing."""
    performance_results = {}
    
    # Test single insert performance
    start = time.time()
    CRUD.insert(table='documents', model=Document, data=sample_doc)
    performance_results['single_insert'] = time.time() - start
    
    # Test bulk insert performance
    start = time.time()
    CRUD.bulk_insert(table='documents', model=Document, data_list=sample_docs)
    performance_results['bulk_insert'] = time.time() - start
    
    # Test query performance
    start = time.time()
    results = CRUD.get(table='documents', model=Document)
    performance_results['simple_query'] = time.time() - start
    
    # Validate performance benchmarks
    assert performance_results['single_insert'] < 0.01
    assert performance_results['bulk_insert'] < 5.0
    assert performance_results['simple_query'] < 0.05
```

## Error Handling Tests

### Data Validation Testing
```python
def test_model_validation():
    """Test Pydantic model validation and error handling."""
    # Test invalid data handling
    with pytest.raises(ValidationError):
        BiomedicalEntityBlock(
            block_id="",  # Invalid: empty string
            doc_id="valid_doc",
            medications=123  # Invalid: not a list
        )
    
    # Test required field validation
    with pytest.raises(ValidationError):
        Document(
            # Missing required fields
            title="Test Document"
        )
```

### Database Constraint Testing
```python
def test_foreign_key_constraints():
    """Test database foreign key constraint enforcement."""
    # Test invalid foreign key reference
    with pytest.raises(IntegrityError):
        CRUD.insert(
            table='pdf_blocks',
            model=PDFBlock,
            data=PDFBlock(
                doc_id="nonexistent_doc",  # Invalid foreign key
                text="Sample text"
            )
        )
```

## Running the Tests

### Individual Test Execution
```bash
# Run specific test file
pytest tests/db/test_create.py -v

# Run specific test function
pytest tests/db/test_fetch.py::test_fetch_entities -v

# Run with coverage
pytest tests/db/ --cov=BFHTW.utils.crud --cov-report=html
```

### Full Test Suite


### Continuous Integration


## Quality Assurance


*Comprehensive testing ensures reliable, high-performance database operations for biomedical document processing workflows.*