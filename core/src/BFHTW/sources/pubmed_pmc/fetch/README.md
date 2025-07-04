# PubMed PMC Data Fetcher

This repository contains a set of Python scripts designed to fetch and process data from the PubMed Central (PMC) database. The primary focus is on obtaining article metadata, file lists, and related resources from PMC's FTP server.

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Modules](#modules)
- [Usage](#usage)
- [Dependencies](#dependencies)

## Overview

The scripts in this repository are built around a base class, `BaseFTPFetcher`, which provides common functionality for downloading and validating CSV files from the PMC FTP server. Specialized fetchers extend this base class to retrieve specific datasets, such as PMC IDs and file lists. Additionally, there is functionality for downloading complete articles in tarball format and extracting relevant files from them.

## Directory Structure

```plaintext
BFHTW/
├── sources/
│   └── pubmed_pmc/
│       ├── fetch/
│       │   ├── base_fetcher.py         # Base class for fetching data
│       │   ├── fetch_PMCID_mapping.py   # Fetcher for PMC ID mappings
│       │   ├── fetch_file_list.py       # Fetcher for file lists
│       │   └── fetch_xml_paths.py       # Fetcher for XML paths and mappings
│       ├── pmc_article_downloader.py    # Downloads and extracts articles
│       └── merge_article_paths_with_pmids.py # Merges article paths with PMIDs
└── utils/
    └── logs.py                         # Logging utilities
```

## Modules

### 1. `base_fetcher.py`

Contains the `BaseFTPFetcher` class that handles common tasks like creating storage directories, downloading files, and loading CSV data into DataFrames. This class is the foundation for other specific fetchers.

### 2. `fetch_PMCID_mapping.py`

Implements the `PMCIDMappingFetcher` class, which fetches the PMC ID mappings from the PMC FTP server. It ensures that the expected columns are validated upon loading the data.

### 3. `fetch_file_list.py`

Defines the `FileListFetcher` class, which retrieves the list of files available in the PMC repository. It includes functionality to fetch new articles since the last download.

### 4. `pmc_article_downloader.py`

Contains the `PMCArticleDownloader` class, responsible for downloading and extracting articles from the PMC FTP server. It handles tarball files and extracts PDF documents from them.

### 5. `fetch_xml_paths.py`

Defines the `FetchXML` class, which interfaces with the PMC API to retrieve article paths based on provided PMIDs. It integrates with the `PMCAPIClient` to perform searches and matches.

## Usage

To use these modules, you can instantiate the respective fetcher classes and call their methods to download and process data. For example:

```python
from BFHTW.sources.pubmed_pmc.fetch.fetch_PMCID_mapping import PMCIDMappingFetcher

fetcher = PMCIDMappingFetcher()
pmc_data = fetcher.fetch()
```

Ensure that the necessary dependencies are installed before running the scripts.

## Dependencies

- `requests`
- `pandas`

Make sure to install the required libraries using pip:

```bash
pip install requests pandas
``` 

## License

This project is licensed under the MIT License. See the LICENSE file for more details.