# PubMed Parser

This repository contains a set of Python modules designed to parse PubMed Central-style NXML (XML-based) files. The primary goal is to extract structured information from these files, including metadata and content blocks, which can then be utilized in various biomedical applications.

## Contents

The folder includes the following Python files:

- **pubmed_parser.py**: Contains the implementation of the `PubMedNXMLParser` class, which extracts content blocks from NXML documents.
- **nxml_parser.py**: Defines a more detailed `PubMedNXMLParser` class that extends the base parser, providing functions to extract metadata like authors, publication dates, and journal information.
- **base_parser.py**: An abstract base class `BaseNXMLParser` that provides a standard interface and core utilities for parsing NXML documents. It defines required methods for subclasses to implement.

## Structure

### 1. `base_parser.py`
- **Class**: `BaseNXMLParser`
  - Abstract base class for NXML parsers.
  - Contains methods for metadata extraction, utility functions, and a method to save metadata.
  - Requires subclasses to implement methods for extracting specific metadata fields.

### 2. `pubmed_parser.py`
- **Class**: `PubMedNXMLParser`
  - Inherits from `BaseNXMLParser`.
  - Implements the `extract_blocks` method to yield content blocks from the NXML file.
  - Extracts section titles and text from paragraphs within the sections.

### 3. `nxml_parser.py`
- **Class**: `PubMedNXMLParser`
  - Extends the functionality of the parser by implementing additional metadata extraction methods including:
    - `get_external_id`
    - `get_publication_date`
    - `extract_authors`
    - `get_journal`
    - `get_doi`
    - `get_clinical_trial_ref`
  - Implements the `extract_blocks` method for yielding structured block objects, including token counts and character positions for each paragraph.
  - Provides a method to construct a `Document` object containing comprehensive metadata about the parsed document.

## Usage
To use the parsers, instantiate the `PubMedNXMLParser` class from `nxml_parser.py` with the required parameters (file path, document ID, source database, etc.) and call the relevant methods to extract metadata and content blocks.

## Requirements
- Python 3.x
- `lxml`
- `transformers`

## License
This project is licensed under the MIT License. See the LICENSE file for details.