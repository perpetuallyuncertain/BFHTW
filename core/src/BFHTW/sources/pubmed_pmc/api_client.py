import requests
import json
from typing import Optional, List
from pathlib import Path

from BFHTW.utils.logs import get_logger

L = get_logger()

ROOT_DIR = Path(__file__).parent.parent.parent


class PMCAPIClient:
    def __init__(
        self,
        url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        search_terms_file_path: str = "search_terms.json",
        db: str = "pmc",
        retmax: Optional[int] = 1_000_000,
        retmode: str = "json"
    ):
        self.url = url
        self.search_terms_file_path = search_terms_file_path
        self.db = db
        self.retmax = retmax
        self.retmode = retmode

        self.search_terms = self.get_search_terms()
        self.pmc_ids = self.make_pmc_request(self.search_terms)

    def get_search_terms(self) -> List[str]:
        file_path = ROOT_DIR / "sources" / "pubmed_pmc" / self.search_terms_file_path
        
        with open(file_path, "r") as f:
            search_terms = json.load(f)

        if not isinstance(search_terms, list) or not search_terms:
            raise ValueError("search_terms.json must contain a non-empty list of strings.")

        return search_terms

    def make_pmc_request(self, search_terms: List[str]) -> List[str]:
        if len(search_terms) > 1:
            formatted_terms = [
            f'"{term}"' if " " in term else term
            for term in search_terms
        ]
            query = f'({" OR ".join(formatted_terms)})'

        else:
            query = search_terms[0].replace(" ", "+")

        if not self.retmax:
             params = {
            "db": self.db,
            "term": query,
            "retmode": self.retmode
        }

        else:    
            params = {
                "db": self.db,
                "term": query,
                "retmax": self.retmax,
                "retmode": self.retmode
            }

        response = requests.get(self.url, params=params)
        response.raise_for_status()
        data = response.json()
        L.info(f"Search retrieved {len(data.get('esearchresult', {}).get('idlist', []))} results")

        return data.get("esearchresult", {}).get("idlist", [])

