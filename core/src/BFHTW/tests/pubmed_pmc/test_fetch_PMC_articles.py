import pytest
import pandas as pd

from BFHTW.sources.pubmed_pmc.fetch_pmc_articles import FetchPMCArticles
from BFHTW.utils.logs import get_logger


L = get_logger()

article_getter = FetchPMCArticles()

@pytest.mark.unit
def test_article_getter():
    todays_snapshot = article_getter.fetch_new_pmc_articles()
    assert isinstance(todays_snapshot, pd.DataFrame), "todays_snapshot is not a DataFrame"

