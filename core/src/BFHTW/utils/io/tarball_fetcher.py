# src/BFHTW/utils/io/tarball_fetcher.py

import tarfile
import requests
from pathlib import Path
from urllib.parse import urljoin
from BFHTW.utils.logs import get_logger

L = get_logger()

class TarballFetcher:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def download(self, url: str, target_path: Path) -> None:
        """Download a tar.gz file from a URL."""
        L.info(f"Downloading: {url}")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(target_path, "wb") as f:
            for i, chunk in enumerate(response.iter_content(chunk_size=8192)):
                if chunk:
                    f.write(chunk)
                    if i % 25 == 0:
                        L.debug(f"Downloaded ~{i * 8192} bytes...")

        L.info(f"Saved to: {target_path}")

    def extract(self, tar_path: Path, extract_to: Path) -> None:
        """Extract all contents of a tar.gz file."""
        extract_to.mkdir(parents=True, exist_ok=True)
        L.info(f"Extracting: {tar_path} → {extract_to}")

        try:
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=extract_to)
        except tarfile.TarError as e:
            raise RuntimeError(f"Tar extraction error: {e}")

        if not any(extract_to.iterdir()):
            raise RuntimeError(f"Extraction failed — directory is empty: {extract_to}")

        L.info("Extraction complete.")

    def find_first_pdf(self, extract_dir: Path) -> Path | None:
        """Search for the first PDF file in the extracted directory."""
        pdfs = list(extract_dir.rglob("*.pdf"))
        if not pdfs:
            L.warning(f"No PDF found in {extract_dir}")
            return None
        return pdfs[0]
