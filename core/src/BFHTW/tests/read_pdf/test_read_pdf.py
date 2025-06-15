import pytest
from pathlib import Path
import pdb

from BFHTW.utils.pdf_reader.read_pdf import ReadPDF
from BFHTW.utils.logs import get_logger

L = get_logger()

@pytest.mark.dev
def test_read_pdf():

    result = ReadPDF.get_pdf_data(
        pdf_filename="test_data/test1.pdf",
    )
    assert result is not None, "PDF data extraction failed"
    assert result.metadata is not None, "PDF metadata extraction failed"
    assert result.blocks is not None, "PDF blocks extraction failed"



