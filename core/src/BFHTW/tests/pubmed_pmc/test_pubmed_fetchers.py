import pytest
from BFHTW.sources.pubmed_pmc.fetch.fetch_file_list import FileListFetcher

@pytest.mark.live
def test_fetch_file_list_smoke(tmp_path):
    fetcher = FileListFetcher()
    
    # Monkeypatch fetcher's internal cache dir to tmp_path
    fetcher.ROOT_DIR = tmp_path
    fetcher.ensure_base_dir()

    df = fetcher.fetch()

    # Basic shape/sanity checks
    assert not df.empty
    assert "pmcid" in df.columns
    assert df["pmcid"].notnull().all()

@pytest.mark.live
def test_fetch_new_articles_when_snapshots_exist(tmp_path):
    fetcher = FileListFetcher()
    fetcher.ROOT_DIR = tmp_path
    fetcher.en()

    # Force one snapshot to exist
    df = fetcher.fetch()
    snapshot_path = fetcher.get_latest_path()
    snapshot_path.write_text(df.to_csv(index=False))  # simulate prior snapshot

    new_df = fetcher.fetch_new_articles()

    assert isinstance(new_df, pd.DataFrame)
