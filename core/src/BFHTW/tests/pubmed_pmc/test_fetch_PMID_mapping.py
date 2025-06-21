import pytest
import pandas as pd
from BFHTW.sources.pubmed_pmc.fetch.fetch_PMCID_mapping import PMCIDMappingFetcher

@pytest.mark.skip
def test_fetch_pmcid_mapping_smoke(tmp_path, monkeypatch):
    fetcher = PMCIDMappingFetcher()

    # Monkeypatch base_dir to isolate snapshot writes
    monkeypatch.setattr(
        fetcher.__class__,
        "base_dir",
        property(lambda self: tmp_path)
    )
    fetcher.storage_dir = fetcher._make_storage_dir("data")

    df = fetcher.fetch()
    
    assert not df.empty
    assert "PMID" in df.columns
    assert "PMCID" in df.columns
    assert "DOI" in df.columns
    assert df["PMID"].notnull().any()
