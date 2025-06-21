from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional
import requests
import pandas as pd
import mimetypes

class BaseFTPFetcher:
    def __init__(
        self,
        filename_prefix: str,
        storage_subdir: str = "data",
        filetype: str = "csv",  # or "csv.gz"
        expected_columns: Optional[list|str] = None
    ):
        from BFHTW.utils.logs import get_logger
        self.L = get_logger()
        self.filename_prefix = filename_prefix
        self.filetype = filetype
        self.expected_columns = expected_columns or []
        self.ROOT_DIR = self.base_dir
        self.storage_dir = self._make_storage_dir(storage_subdir)

    def _make_storage_dir(self, subdir: str) -> Path:
        storage_path = self.ROOT_DIR / "sources" / "pubmed_pmc" / subdir
        storage_path.mkdir(parents=True, exist_ok=True)
        return storage_path

    def _today_str(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parents[3]
    
    def get_suffix(self) -> str:
        return ".csv.gz" if self.filetype == "csv.gz" else ".csv"

    def get_latest_path(self) -> Path:
        return self.storage_dir / f"{self.filename_prefix}_{self._today_str()}{self.get_suffix()}"

    def get_all_snapshots(self) -> list[Path]:
        return sorted(self.storage_dir.glob(f"{self.filename_prefix}_*{self.get_suffix()}"))

    def download_file(self, url: str, target_path: Path):
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(target_path, "wb") as f:
                    print(f"Downloading {target_path.name}", end="", flush=True)
                    for i, chunk in enumerate(r.iter_content(chunk_size=8192)):
                        if chunk:
                            f.write(chunk)
                            if i % 100 == 0:
                                print(".", end="", flush=True)
                    print(" done.")
        except Exception as e:
            self.L.error(f"Failed to download {url}", exc_info=True)
            raise

    def load_csv(self, path: Path) -> pd.DataFrame:
        compression = "gzip" if path.suffix == ".gz" else None
        try:
            df = pd.read_csv(path, compression=compression)
            
            if df.empty:
                raise ValueError(f"Loaded DataFrame is empty from {path}")
            if self.expected_columns and not set(self.expected_columns).issubset(df.columns):
                raise ValueError(f"Expected columns {self.expected_columns} not found in {path.name}")
            return df
        except Exception as e:
            self.L.error(f"Failed to load or validate CSV file {path.name}", exc_info=True)
            raise

    def fetch_and_cache(self, url: str) -> pd.DataFrame:
        local_path = self.get_latest_path()
        if not local_path.exists():
            self.L.info(f"Downloading fresh file: {self.filename_prefix}")
            self.download_file(url, local_path)
        else:
            self.L.info(f"File already exists: {local_path.name}")

        return self.load_csv(local_path)
