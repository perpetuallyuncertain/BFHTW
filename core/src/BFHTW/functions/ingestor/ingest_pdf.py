from pathlib import Path
from BFHTW.utils.pdf_reader.read_pdf import ReadPDF
from BFHTW.models.articles.pydantic import PDFMetadata, BlockData
from BFHTW.utils.crud.crud import CRUD
from BFHTW.utils.logs import get_logger
from typing import Tuple

L = get_logger()

def extraction(pdf_path: Path) -> Tuple[PDFMetadata, BlockData]:
    """
    Generic processor for a single PDF file.
    Extracts metadata and blocks, and saves them into SQL.
    
    Args:
        pdf_path (Path): Full path to the PDF file.
    
    Returns:
        Tuple[str, int]: Document ID and number of blocks processed.
    """
    # Step 1: Parse PDF content
    read_result = ReadPDF.get_pdf_data(pdf_filename=str(pdf_path))

    if not read_result or not read_result.metadata or not read_result.blocks:
        raise ValueError(f"PDF processing failed for: {pdf_path}")

    # Step 2: Save metadata
    CRUD.create_table_if_not_exists(
        table="pdf_metadata",
        model=PDFMetadata,
        primary_key="doc_id"
    )

    CRUD.insert(table="pdf_metadata", model=PDFMetadata, data=read_result.metadata)

    L.info(f"PDF Metadata saved for Document ID: {read_result.metadata.doc_id}")

    # Ensure blocks table exists
    CRUD.create_table_if_not_exists(
        table="pdf_blocks",
        model=BlockData,
        primary_key="block_id"
    )

    # Step 3: Save blocks
    CRUD.bulk_insert(table="pdf_blocks", model=BlockData, data_list=read_result.blocks)

    L.info(f"Inserted {len(read_result.blocks)} blocks for Document ID: {read_result.metadata.doc_id}")

    return f"Processed PDF with Document ID ({read_result.metadata.doc_id}) and inserted {len(read_result.blocks)} blocks."
