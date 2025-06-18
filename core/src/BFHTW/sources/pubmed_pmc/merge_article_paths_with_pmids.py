import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional

from BFHTW.utils.logs import get_logger

L = get_logger()

def join_mapping_files(base_dir: Optional[Path | None] = None):
    if base_dir is None:
        base_dir = Path(__file__).resolve().parents[2]

    today_str = datetime.now().strftime("%Y-%m-%d")
    data_dir = base_dir / "sources" / "pubmed_pmc" / "data"

    pmid_map_path = data_dir / f"PMC-ids_{today_str}.csv.gz"
    oa_file_list_path = data_dir / f"oa_file_list_{today_str}.csv"

    if not pmid_map_path.exists():
        msg = f"PMID Mapping file doesn't exist at {pmid_map_path}"
        L.error(msg)
        raise FileNotFoundError(msg)
    
    if not oa_file_list_path.exists():
        msg = f"File list doesn't exist at {oa_file_list_path}"
        L.error(msg)
        raise FileNotFoundError(msg)

    pmid_map = pd.read_csv(pmid_map_path, usecols=["PMCID", "PMID"], dtype=str)
    oa_file_list = pd.read_csv(oa_file_list_path, usecols=["Accession ID", "File", "PMID", "License"], dtype=str)

    merged = oa_file_list.merge(pmid_map, left_on="Accession ID", right_on="PMCID")
    return merged