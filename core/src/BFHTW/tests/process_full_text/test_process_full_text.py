import pytest
from BFHTW.functions.pubmed_pipeline.process_new_pubmed import process_full_text

@pytest.mark.unit
def test_process_full_text():
    process_full_text()
