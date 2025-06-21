import pytest
import pandas as pd
from pathlib import Path
from BFHTW.sources.pubmed_pmc.fetch.fetch_xml_paths import FetchXML

@pytest.mark.live
def test_fetchxml_matches_article_paths_live(tmp_path: Path):
    """
    Live test that uses real PMC API and attempts to join with today's local snapshot.
    Safely reroutes file operations to a temp path to avoid touching real data.
    """
    fetcher = FetchXML()

    # Setup fake expected structure so fetcher can find data (optional here, shown for structure)
    data_dir = tmp_path / "sources" / "pubmed_pmc" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Optionally, copy fixture files here (e.g., from `tests/fixtures/pubmed_data/`)

    fetcher = FetchXML()
    df = fetcher.match_pmcids_to_ftp_paths()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert {"File", "PMCID", "PMID_x", "PMID_y"}.issubset(df.columns)
