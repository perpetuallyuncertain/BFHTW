# PDF Block Extractor and Metadata Reader

This repository contains modules for extracting structured text blocks and metadata from PDF files using the PyMuPDF library. The main purpose of these modules is to facilitate the analysis and processing of PDF documents by providing easy access to their content and metadata.

## Contents

- **pdf_block_extractor.py**: Module responsible for extracting structured text blocks from a PDF file.
- **pdf_metadata.py**: Module responsible for reading and extracting high-level metadata from a PDF file.

## Module Descriptions

### pdf_block_extractor.py

This module provides the `PDFBlockExtractor` class, which is responsible for parsing a PDF document and extracting structured blocks of text along with associated metadata. 

#### Key Features:
- Opens a PDF document using the PyMuPDF library.
- Iterates through each page to extract text blocks.
- Each block is encapsulated in a `PDFBlock` object that contains:
  - Unique block ID
  - Document ID
  - Page number
  - Block index
  - Extracted text
  - Bounding box coordinates
  - Font size, name, and color
  - Line count and token count
  - Creation timestamp
  - Processed status

### pdf_metadata.py

This module provides the `PDFReadMeta` class, which focuses on extracting high-level metadata from a PDF file.

#### Key Features:
- Opens a PDF document and retrieves its metadata, including:
  - Title
  - Author
  - Subject
  - Keywords
  - Creator
  - Producer
  - Creation and modification dates
  - Encryption status
  - File path of the PDF

## Usage

To use these modules, instantiate the respective classes and call their methods with the path to the PDF file and an optional document ID. For example:

```python
from pdf_block_extractor import PDFBlockExtractor
from pdf_metadata import PDFReadMeta

# Extract blocks
blocks = PDFBlockExtractor.extract_blocks(Path('path/to/pdf.pdf'), 'document_id')

# Read metadata
metadata = PDFReadMeta.extract_metadata(Path('path/to/pdf.pdf'))
```

## Requirements

- Python 3.x
- PyMuPDF library (install via `pip install PyMuPDF`)

## Logging

Both modules use a logging utility to provide feedback on the extraction process, including warnings and errors, which can be useful for debugging and monitoring.

## License

This project is licensed under the MIT License. See the LICENSE file for details.