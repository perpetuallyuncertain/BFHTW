import pandas as pd
from typing import Optional
from pathlib import Path

from BFHTW.utils.logs import get_logger
from BFHTW.sources.pubmed_pmc.pmc_api_client import PMCAPIClient
from BFHTW.sources.pubmed_pmc.merge_article_paths_with_pmids import join_mapping_files

L = get_logger()

class FetchXML:
    def __init__(
        self, 
        api_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        search_terms_filename: str = "search_terms.json",
        base_dir: Optional[Path] = None
    ):
        # Initialize API client and retrieve PMIDs from search
        self.api_client = PMCAPIClient(url=api_url, search_terms_file_path=search_terms_filename, db="pmc")
        self.pmids = self.api_client.pmc_ids  # should be list[str]
        self.base_dir = base_dir

        # Load merged/filtered mapping table from disk
        self.todays_data = self.get_todays_data()

    def get_todays_data(self) -> pd.DataFrame:
        try:
            return join_mapping_files(base_dir=self.base_dir)
        except Exception as e:
            L.error(f"Failed to join mapping files: {e}")
            raise

    def match_pmcids_to_ftp_paths(
            self,
            pmids: Optional[list[str]] = None,
            todays_data: Optional[pd.DataFrame] = None
            ) -> pd.DataFrame:
        # Use defaults from instance if not provided
        if pmids is None:
            pmids = self.pmids
        if todays_data is None:
            todays_data = self.todays_data

        # Normalize and filter by PMID
        todays_data["PMID_y"] = todays_data["PMID_y"].astype(str).str.replace(r"\.\d+$", "", regex=True)
        cleaned_pmids = [str(pmid).replace(".0", "") for pmid in pmids]
        
        article_paths = todays_data[
            todays_data["PMID_x"].isin(cleaned_pmids) |
            todays_data["PMID_y"].isin(cleaned_pmids)
        ].copy()

        return article_paths
