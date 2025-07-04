# PubMed PMC Data Fetching Tests

This repository contains tests for fetching data from the PubMed Central (PMC) API. The tests are designed to ensure that the various data fetching components work correctly, and they utilize the pytest framework for testing.

## Purpose
The primary purpose of this folder is to validate the functionality of the data fetching mechanisms used to retrieve article paths, PMID mappings, and file lists from the PMC API. These tests ensure that the data retrieval processes are robust and that they handle edge cases appropriately.

## Folder Structure
The folder contains the following test files:

- `test_fetch_xml_paths.py`: Tests the `FetchXML` class that retrieves XML paths for articles from the PMC API and matches them to local data snapshots.
- `test_fetch_PMID_mapping.py`: Tests the `PMCIDMappingFetcher` class which is responsible for fetching mappings between PMIDs and PMCIDs.
- `test_fetch_file_list.py`: Tests the `FileListFetcher` class that retrieves a list of files from the PMC API.

## Test Descriptions

### `test_fetch_xml_paths.py`
- **Test Function**: `test_fetchxml_matches_article_paths_live`
- **Description**: This is a live test that interacts with the PMC API to validate that the fetched XML paths match the expected article paths in a local snapshot. It uses a temporary path to avoid modifying real data.
- **Key Assertions**:
  - The output is a pandas DataFrame.
  - The DataFrame is not empty.
  - The DataFrame contains the expected columns: `File`, `PMCID`, `PMID_x`, `PMID_y`.

### `test_fetch_PMID_mapping.py`
- **Test Function**: `test_fetch_pmcid_mapping_smoke`
- **Description**: This test verifies that the `PMCIDMappingFetcher` retrieves a non-empty DataFrame containing PMID, PMCID, and DOI columns. It uses monkeypatching to isolate the test environment.
- **Key Assertions**:
  - The DataFrame is not empty.
  - The DataFrame contains the columns `PMID`, `PMCID`, and `DOI`.
  - At least one PMID is not null.

### `test_fetch_file_list.py`
- **Test Functions**:
  - `test_fetch_file_list_smoke`
  - `test_fetch_new_articles_when_snapshots_exist`
- **Description**: These tests check the functionality of the `FileListFetcher`. The first test ensures that a non-empty DataFrame with valid `Accession ID` entries is returned. The second test checks that new articles can be fetched when previous snapshots exist, validating the fetching mechanism.
- **Key Assertions**:
  - The DataFrame is not empty.
  - The DataFrame contains the column `Accession ID`.
  - All `Accession ID` values are not null.

## Running the Tests
To run the tests, ensure you have pytest installed. You can execute the tests by running:

```bash
pytest
```

This will discover and run all test files in the directory.

## Dependencies
- `pytest`: The testing framework used to run the tests.
- `pandas`: A library for data manipulation and analysis, used to handle DataFrames in tests.

## Conclusion
These tests provide essential coverage for fetching data from the PMC API, ensuring that the data retrieval mechanisms are functioning correctly and efficiently. By running these tests, developers can maintain confidence in the integrity of the data fetching process.