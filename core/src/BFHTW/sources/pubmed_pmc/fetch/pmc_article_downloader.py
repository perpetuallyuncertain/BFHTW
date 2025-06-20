# src/BFHTW/sources/pubmed_pmc/pmc_article_downloader.py

from pathlib import Path
from urllib.parse import urljoin
from BFHTW.models.pubmed_pmc import PMCArticleMetadata
from BFHTW.utils.io.tarball_fetcher import TarballFetcher

class PMCArticleDownloader:
    def __init__(self, matched_article: PMCArticleMetadata, base_dir: Path | None = None):
        self.article = matched_article
        self.base_dir = base_dir or Path(__file__).resolve().parents[3] / "sources" / "pubmed_pmc" / "temp"
        self.fetcher = TarballFetcher(self.base_dir)

    def run(self) -> tuple[Path, Path]:
        """Download and extract tarball. Return (pdf_path, tarball_path)."""
        ftp_url = self.build_ftp_url()
        tarball_path = self.get_local_path()
        extract_path = self.get_extract_path()

        if not tarball_path.exists():
            self.fetcher.download(ftp_url, tarball_path)
            self.fetcher.extract(tarball_path, extract_path)

        pdf_path = self.fetcher.find_first_pdf(extract_path)
        if not pdf_path:
            raise FileNotFoundError(f"No PDF found in {extract_path}")

        return pdf_path, tarball_path

    def build_ftp_url(self) -> str:
        return urljoin("https://ftp.ncbi.nlm.nih.gov/pub/pmc/", self.article.file_path)

    def get_local_path(self) -> Path:
        return self.base_dir / Path(self.article.file_path).name

    def get_extract_path(self) -> Path:
        return self.base_dir / self.article.accession_id
