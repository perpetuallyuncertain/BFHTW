import pytest
from pathlib import Path

from BFHTW.utils.pdf.pdf_metadata import PDFReadMeta
from BFHTW.utils.logs import get_logger

L = get_logger()

@pytest.mark.unit
def test_read_pdf():

    metadata = PDFReadMeta.extract_metadata(
        pdf_filename="test_data/test1.pdf",
    )
    assert metadata is not None, "PDF data extraction failed"
    assert metadata is not None, "PDF metadata extraction failed"




