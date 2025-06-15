import pandas as pd
import requests
from pathlib import Path
from datetime import datetime

from BFHTW.utils.logs import get_logger

L = get_logger()

class FetchPMCArticles:

    def __init__(self):
        self.storage_dir = self.make_storage_dir()

    def make_storage_dir(self):
        ROOT_DIR = Path(__file__).parent.parent.parent
        storage_dir = ROOT_DIR / "sources" / "pubmed_pmc" / "data"
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir

    def download_file(self, url: str, target_path: Path):
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(target_path, "wb") as f:
                print("Downloading", end="", flush=True)
                for i, chunk in enumerate(r.iter_content(chunk_size=8192)):
                    if chunk:
                        f.write(chunk)
                        if i % 50 == 0:  # Only print every 20 chunks
                            print(".", end="", flush=True)
                print(" done.")

    def fetch_new_pmc_articles(self) -> pd.DataFrame:
        """
        Downloads the latest oa_file_list.csv and compares with the previously saved one.
        Returns a DataFrame of new articles only.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_file = self.storage_dir / f"oa_file_list_{today_str}.csv"

        # Only download if today's file doesn't already exist
        if not today_file.exists():
            L.info("Downloading latest oa_file_list.csv from PMC FTP...")
            self.download_file("https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.csv", today_file)
        else:
            L.info("Today's oa_file_list.csv already exists. Skipping download.")

        today_df = pd.read_csv(today_file)

        # Check for a previous file
        all_snapshots = sorted(self.storage_dir.glob("oa_file_list_*.csv"))
        if len(all_snapshots) < 2:
            L.info("No prior snapshot found. Returning full list.")
            return today_df

        else:
            previous_file = all_snapshots[-2]
            prev_df = pd.read_csv(previous_file)

            # Compare by PMC ID to find new entries
            new_df = today_df[~today_df["pmcid"].isin(prev_df["pmcid"])].copy()
            L.info(f"Found {len(new_df)} new articles.")
            return new_df


# Run the fetcher if this script is executed directly
if __name__ == "__main__":
    fetcher = FetchPMCArticles()
    df = fetcher.fetch_new_pmc_articles()
    print(df.head())
