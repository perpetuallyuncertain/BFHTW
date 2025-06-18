import pytest
from _pytest.monkeypatch import MonkeyPatch
import pandas as pd
from BFHTW.sources.pubmed_pmc.fetch.fetch_file_list import FileListFetcher

@pytest.mark.skip
def test_fetch_file_list_smoke(tmp_path, monkeypatch: MonkeyPatch):
    fetcher = FileListFetcher()

    # Monkeypatch base_dir property
    monkeypatch.setattr(
        fetcher.__class__,
        "base_dir",
        property(lambda self: tmp_path)
    )

    # Reinitialize storage_dir to use new base_dir
    fetcher.storage_dir = fetcher._make_storage_dir("data")

    df = fetcher.fetch()

    assert not df.empty
    assert "Accession ID" in df.columns
    assert df["Accession ID"].notnull().all()

@pytest.mark.skip
def test_fetch_new_articles_when_snapshots_exist(tmp_path, monkeypatch: MonkeyPatch):
    fetcher = FileListFetcher()

    monkeypatch.setattr(
        fetcher.__class__,
        "base_dir",
        property(lambda self: tmp_path)
    )
    fetcher.storage_dir = fetcher._make_storage_dir("data")

    # First fetch = snapshot
    df = fetcher.fetch()
    snapshot_path = fetcher.get_latest_path()
    snapshot_path.write_text(df.to_csv(index=False))

    # Now call fetch_new_articles()
    new_df = fetcher.fetch_new_articles()

    assert isinstance(new_df, pd.DataFrame)


