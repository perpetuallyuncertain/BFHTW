# PubMed Download and Parse

This repository contains scripts for downloading and processing articles from the PubMed Central (PMC) database. The scripts facilitate the fetching of article metadata, downloading of article files, and extraction of relevant text data for further analysis.

## Contents

- **pubmed_download_and_parse.py**: This script is responsible for fetching unprocessed article files from PMC, extracting their contents, and performing Named Entity Recognition (NER) and embedding generation on the extracted text blocks.
- **pubmed_fetch_metadata.py**: This script fetches metadata related to PMC articles, including the latest file lists and PMCID mappings, and saves this information in a database.

## Structure

### pubmed_download_and_parse.py

1. **Logging**: Initializes logging for tracking the process.
2. **Fetch Unprocessed Paths**: Retrieves a list of unprocessed PMC article paths from the database.
3. **Download TAR.GZ**: Downloads the article files from the PMC FTP server.
4. **Extract Contents**: Extracts the downloaded TAR.GZ files to a temporary directory.
5. **Locate PDF or NXML**: Searches for PDF or NXML files in the extracted contents.
6. **PDF Processing**: If a PDF file is found, it extracts metadata and text blocks from the PDF.
7. **Insert Metadata and Blocks**: Saves the extracted metadata and text blocks into the database.
8. **Named Entity Recognition**: Applies NER to the text blocks to identify keywords.
9. **Embedding Generation**: Generates embeddings for the text blocks using BioBERT.
10. **Save NER and Embeddings**: Inserts the identified keywords and generated embeddings into the database.
11. **Cleanup**: Cleans up temporary files and directories after processing.

### pubmed_fetch_metadata.py

1. **Logging**: Initializes logging for tracking the process.
2. **Fetch New Articles**: Fetches the latest article file list from the PMC FTP server.
3. **Fetch PMCID Mapping**: Retrieves the latest PMCID mapping file to link PMCIDs to their respective FTP paths.
4. **Fetch XML Paths**: Matches PMCIDs to their corresponding FTP paths for downloading.
5. **Save List to SQL**: Saves the fetched article paths and metadata into the database.

## Usage

To run the scripts, ensure that you have the necessary dependencies installed and the database configured. Execute the scripts in the following order:

1. `pubmed_fetch_metadata.py`: To fetch and store article metadata.
2. `pubmed_download_and_parse.py`: To download and process the articles based on the fetched metadata.

## Requirements

- Python 3.x
- Required Python packages (refer to the project's requirements.txt or setup.py for specific packages)

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- NCBI for providing the PubMed Central database.
- The developers and contributors to the BioBERT framework.