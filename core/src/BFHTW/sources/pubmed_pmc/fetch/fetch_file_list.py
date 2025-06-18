from BFHTW.sources.pubmed_pmc.fetch.base_fetcher import BaseFTPFetcher
import pandas as pd

class FileListFetcher(BaseFTPFetcher):
    def __init__(self):
        super().__init__(filename_prefix="oa_file_list")

    def fetch(self) -> pd.DataFrame:
        url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.csv"
        today_path = self.get_latest_path()
        
        if not today_path.exists():
            self.L.info("Fetching oa_file_list.csv")
            self.download_file(url, today_path)
        else:
            self.L.info("File already downloaded")

        return self.load_csv(today_path)

    def fetch_new_articles(self) -> pd.DataFrame:
        df = self.fetch()
        snapshots = self.get_all_snapshots()
        if len(snapshots) < 2:
            return df
        prev_df = self.load_csv(snapshots[-2])
        return df[~df["Accession ID"].isin(prev_df["Accession ID"])]
