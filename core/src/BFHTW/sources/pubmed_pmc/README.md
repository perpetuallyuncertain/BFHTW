# README

## Overview
This repository contains scripts and configuration files for processing and fetching data from PubMed Central (PMC) and related resources. The main functionalities include merging article paths with their corresponding PubMed IDs (PMIDs), fetching abstracts from PubMed, and managing search terms for querying the PMC API.

## Contents
The folder includes the following files:

- **merge_article_paths_with_pmids.py**: A Python script that merges article paths with PMIDs based on mapping files. It checks for the existence of necessary CSV files and performs the merging operation using Pandas.

- **search_terms.json**: A JSON file containing a list of search terms related to liver cancer and associated pathways. This file is used by the PMC API client to perform searches.

- **pmc_api_client.py**: A Python class that interacts with the PMC API to fetch PMIDs based on search terms defined in `search_terms.json`. It handles the construction of API requests and manages the retrieval of data.

- **fetch_abstracts.py**: A script that fetches the abstracts of articles from PubMed using their PMIDs. It processes requests in batches to comply with API limits.

## Structure
The folder structure is as follows:

```
.
├── merge_article_paths_with_pmids.py
├── search_terms.json
├── pmc_api_client.py
└── fetch_abstracts.py
```

## Usage
1. **Merging Article Paths with PMIDs**: Run `merge_article_paths_with_pmids.py` to merge the article paths with their PMIDs. Ensure the required CSV files are present in the specified `sources/pubmed_pmc/data` directory.

2. **Fetching PMIDs**: Use the `PMCAPIClient` class from `pmc_api_client.py` to fetch PMIDs based on the search terms provided in `search_terms.json`.

3. **Fetching Abstracts**: Call the `fetch_abstracts` function from `fetch_abstracts.py` with a list of PMIDs to retrieve their abstracts.

## Requirements
- Python 3.x
- `pandas` library for data manipulation
- `requests` library for making HTTP requests

## Logging
The scripts utilize a logging utility from `BFHTW.utils.logs` to log important events and errors, ensuring better traceability and debugging.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.