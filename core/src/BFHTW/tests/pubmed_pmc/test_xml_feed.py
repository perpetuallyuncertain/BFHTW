import pytest
import pandas as pd
from BFHTW.sources.pubmed_pmc.fetch_xml_data import FetchXML

@pytest.mark.unit
def test_xml_feed():
    fetcher = FetchXML()
    matched_articles = fetcher.match_pmcids_to_ftp_paths()
    assert isinstance(matched_articles, pd.DataFrame)
    print(matched_articles.head())