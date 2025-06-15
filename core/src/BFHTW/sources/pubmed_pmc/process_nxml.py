import tarfile
import requests
from pathlib import Path
from BFHTW.utils.logs import get_logger
from BFHTW.models.pubmed_pmc.pydantic import PMCArticleMetadata

L = get_logger()

class FetchPMCFullText:
    def __init__(self, matched_article: PMCArticleMetadata):
        self.article = matched_article

        ROOT_DIR = Path(__file__).parent.parent.parent
        self.output_dir = ROOT_DIR / "sources" / "pubmed_pmc" / "temp"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> tuple[Path, Path]:
        """Download and extract tarball, return (pdf_path, tarball_path)."""
        ftp_url = self.build_ftp_url()
        tarball_path = self.get_local_path()

        if not tarball_path.exists():
            self.download_tarball(ftp_url, tarball_path)
            self.extract_tarball(tarball_path, self.get_extract_path())

        pdf_path = self.find_pdf(self.get_extract_path())
        if not pdf_path:
            raise FileNotFoundError(f"No PDF found in {self.get_extract_path()}")

        return pdf_path, tarball_path

    def build_ftp_url(self) -> str:
        """Build the FTP download URL from file path."""
        return f"https://ftp.ncbi.nlm.nih.gov/pub/pmc/{self.article.file_path}"

    def get_local_path(self) -> Path:
        """Determine the local path where the tar.gz should be saved."""
        filename = Path(self.article.file_path).name
        return self.output_dir / filename

    def get_extract_path(self) -> Path:
        """Get the local folder path to extract the tar contents into."""
        return self.output_dir / self.article.accession_id

    def download_tarball(self, url: str, target_path: Path):
        """Download tarball from FTP to local filesystem."""
        print(f"Downloading: {url}")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(target_path, "wb") as f:
            for i, chunk in enumerate(response.iter_content(chunk_size=8192)):
                if chunk:
                    f.write(chunk)
                    if i % 25 == 0:
                        print(".", end="", flush=True)
        print(f"Saved to: {target_path}")

    def extract_tarball(self, tar_path: Path, extract_to: Path):
        """Extract all contents from the tar.gz file."""
        extract_to.mkdir(parents=True, exist_ok=True)
        print(f"Extracting: {tar_path} → {extract_to}")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_to)
        print("Extraction complete.")
    
    def find_pdf(self, extract_dir: Path) -> Path | None:
        """Recursively search for the first PDF file in the extracted directory."""
        pdf_files = list(extract_dir.rglob("*.pdf"))
        if not pdf_files:
            L.warning(f"No PDF found in {extract_dir}")
            return None
        return pdf_files[0]
