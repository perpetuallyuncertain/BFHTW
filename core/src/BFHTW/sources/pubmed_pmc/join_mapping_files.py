import pandas as pd
from pathlib import Path
from datetime import datetime

from BFHTW.utils.logs import get_logger

L = get_logger()

def join_mapping_files():

    ROOT_DIR = Path(__file__).parent.parent.parent
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    pmid_map_path = ROOT_DIR / "sources" / "pubmed_pmc" / "data" / f"PMC-ids_{today_str}.csv"

    if pmid_map_path.exists():
        pmid_map = pd.read_csv(pmid_map_path, usecols=["PMCID", "PMID"], dtype=str)
    else:
        L.error(f"PMID Mapping file doesn't exist at {pmid_map_path}")

    oa_file_list_path = ROOT_DIR / "sources" / "pubmed_pmc" / "data" / f"oa_file_list_{today_str}.csv"

    if oa_file_list_path.exists():
        oa_file_list = pd.read_csv(oa_file_list_path, usecols=["Accession ID", "File", "PMID", "License"], dtype=str)
    else:
        L.error(f"File list doesn't exist at {oa_file_list_path}")

    merged = oa_file_list.merge(pmid_map, left_on="Accession ID", right_on="PMCID")

    return merged


