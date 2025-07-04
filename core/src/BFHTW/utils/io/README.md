# Tarball Fetcher

The `Tarball Fetcher` is a utility designed to download, extract, and locate PDF files from tar.gz archives. This module is part of the `BFHTW` project and is located in the `src/BFHTW/utils/io/` directory.

## Contents

The main components of this utility are encapsulated in the `TarballFetcher` class, which provides methods for:

- **Downloading** tar.gz files from a specified URL.
- **Extracting** contents from downloaded tar.gz files.
- **Finding** the first PDF file in the extracted directory.

## Structure

### Class: `TarballFetcher`

- **Initialization**  
  `__init__(self, base_dir: Path)`  
  Initializes the `TarballFetcher` with a base directory where downloaded files will be stored. Creates the directory if it does not exist.

- **Method: `download`**  
  `download(self, url: str, target_path: Path) -> Path`  
  Downloads a tar.gz file from the provided URL and saves it to the specified target path. Logs the download progress and raises an error if the download fails.

- **Method: `extract`**  
  `extract(self, tar_path: Path, extract_to: Path) -> None`  
  Extracts the contents of the specified tar.gz file into the provided directory. Validates the extraction and logs the process. Raises an error if extraction fails.

- **Method: `find_first_pdf`**  
  `find_first_pdf(self, extract_dir: Path) -> Path | None`  
  Searches for the first PDF file in the extracted directory and returns its path. Logs a warning if no PDF files are found.

## Usage

To use the `TarballFetcher`, you need to create an instance by passing a base directory to the constructor. Then you can call the `download`, `extract`, and `find_first_pdf` methods as needed. 

Example:
```python
from pathlib import Path
from BFHTW.utils.io.tarball_fetcher import TarballFetcher

fetcher = TarballFetcher(base_dir=Path("/path/to/base_dir"))

# Download a tar.gz file
fetcher.download("http://example.com/file.tar.gz", Path("/path/to/save/file.tar.gz"))

# Extract the downloaded file
fetcher.extract(Path("/path/to/save/file.tar.gz"), Path("/path/to/extract/"))

# Find the first PDF
pdf_path = fetcher.find_first_pdf(Path("/path/to/extract/"))
```  

## Logging

The utility uses a logger to record its operations. Make sure to configure the logging appropriately in your application to capture these logs.

## Requirements

- Python 3.x
- `requests` library for handling HTTP requests.
- Access to a filesystem where the specified directories can be created and written to.