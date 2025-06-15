import requests
from xml.etree import ElementTree as ET

def fetch_abstracts(pmids: list[str]) -> list[dict]:
    abstracts = []
    batch_size = 200  # Entrez max is 200 per call for efetch
    for i in range(0, len(pmids), batch_size):
        batch = ",".join(pmids[i:i+batch_size])
        response = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={
                "db": "pubmed",
                "id": batch,
                "retmode": "xml"
            }
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID")
            title = article.findtext(".//ArticleTitle")
            abstract = article.findtext(".//AbstractText")
            abstracts.append({"pmid": pmid, "title": title, "abstract": abstract})
    return abstracts
