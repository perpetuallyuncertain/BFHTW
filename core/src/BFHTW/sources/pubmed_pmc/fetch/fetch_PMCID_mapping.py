from BFHTW.sources.pubmed_pmc.fetch.base_fetcher import BaseFTPFetcher
class PMCIDMappingFetcher(BaseFTPFetcher):
    def __init__(self):
        super().__init__(
            filename_prefix="PMC-ids",
            filetype="csv.gz",
            expected_columns=["pmid", "pmcid", "doi"]
        )

    def fetch(self):
        url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz"
        today_path = self.get_latest_path()

        if not today_path.exists():
                self.L.info
        return self.fetch_and_cache(url)
