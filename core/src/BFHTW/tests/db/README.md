# BFHTW Testing Suite

This repository contains a suite of tests for the BFHTW (Biomedical Framework for Textual Health Workflows) project. The tests are designed to validate the functionality of various CRUD operations related to PDF metadata extraction and processing.

## Purpose
The purpose of this testing suite is to ensure that the CRUD operations for handling PDF metadata and other biomedical entities function correctly. This includes creating, fetching, and processing data from the database, as well as verifying the integrity and structure of the data being handled.

## Contents
The testing suite consists of the following files:

- `test_create.py`: Contains unit tests for creating PDF metadata entries in the database.
- `test_fetch.py`: Contains development tests for fetching data from the database and verifying its integrity.
- `test_get_unprocessed.py`: Contains unit tests for retrieving unprocessed blocks from the database based on user input.

## File Structure
```plaintext
BFHTW/
├── utils/
│   └── crud/
│       └── crud.py
├── models/
│   ├── pdf_extraction.py
│   ├── bio_medical_entity_block.py
│   └── pubmed_pmc.py
├── test_data/
│   └── test_metadata.json
├── tests/
│   ├── test_create.py
│   ├── test_fetch.py
│   └── test_get_unprocessed.py
└── README.md
```

## Test Descriptions
- **`test_create.py`**:  
  - **Function**: `test_create_pdf_metadata`
  - **Description**: Tests the creation of PDF metadata in the database. It reads test data from a JSON file, initializes the metadata model, and verifies that a new record can be inserted successfully.

- **`test_fetch.py`**:  
  - **Function**: `test_fetch`
  - **Description**: Tests the fetching of data from the `keywords` table in the database. It checks that data is returned, verifies the data type, and ensures that a DataFrame can be created from the fetched data.

- **`test_get_unprocessed.py`**:  
  - **Function**: `test_get_unprocessed`
  - **Description**: Tests the retrieval of unprocessed blocks from the database. It prompts for a table name and marker label, then verifies that the returned data is a DataFrame.

## Running the Tests
To run the tests, ensure you have `pytest` installed and execute the following command in the root directory of the project:

```bash
pytest tests/
```

## Conclusion
This testing suite provides essential coverage for the CRUD operations within the BFHTW project, ensuring that data handling and processing functions as expected. Contributions to enhance the test coverage or functionality are welcome!