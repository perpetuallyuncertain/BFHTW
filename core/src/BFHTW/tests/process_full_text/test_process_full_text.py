import pytest
from BFHTW.functions.pubmed_pipeline.process_new_pubmed import process_full_text

@pytest.mark.dev
def test_process_full_text():
    process_full_text()
