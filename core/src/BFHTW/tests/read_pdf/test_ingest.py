import pytest
from pathlib import Path

from core.src.BFHTW.ingest.ingest_pdf import extraction
from BFHTW.utils.logs import get_logger

L = get_logger()

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

@pytest.mark.unit
def test_read_pdf():

    pdf_file="test_data/test1.pdf"
    result = extraction(
        pdf_path=ROOT_DIR / pdf_file
    )
    assert result is not None, "PDF data extraction failed"
    print(result)



