import pytest
import pandas as pd

from BFHTW.utils.logs import get_logger
from BFHTW.sources.pubmed_pmc.fetch_PMID_mapping import Fetch_PMID_Mapping

L = get_logger()

getter = Fetch_PMID_Mapping()

@pytest.mark.unit
def test_get_mapping():
    todays_mapping = getter.fetch_new_pmid_mapping()
    assert isinstance(todays_mapping, pd.DataFrame), "Data is dataframe."