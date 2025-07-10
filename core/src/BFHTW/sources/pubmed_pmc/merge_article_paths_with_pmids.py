"""
DEPRECATED: Legacy PMC data merging functionality.

This module is deprecated and will be removed in a future version.
Its functionality has been integrated into the unified data source architecture:
- BFHTW.pipelines.data_sources.pmc_source.PMCDataSource

Please use the new PMC data source instead:
```python
from BFHTW.pipelines.data_sources.pmc_source import create_pmc_source

# Create PMC source
pmc_source = create_pmc_source()

# Get merged data (equivalent to join_mapping_files)
merged_data = pmc_source._get_merged_data()
```
"""
import warnings
"""
DEPRECATED: This module has been superseded by the unified data source architecture.

This file contains legacy logic for merging PMC article paths with PMIDs.
The functionality has been migrated to:
- BFHTW.pipelines.data_sources.pmc_source.PMCDataSource._create_merged_data()

This module is maintained for backward compatibility but will be removed in a future version.
Use the new unified pipeline architecture instead.

Migration guide:
1. Replace direct calls to join_mapping_files() with PMCDataSource.fetch_metadata()
2. Use the pipeline framework instead of standalone scripts
3. All metadata now flows through the Document model and documents table

For more information, see:
- /home/steven/BFHTW/core/src/BFHTW/pipelines/data_sources/
- /home/steven/BFHTW/core/src/MIGRATION_GUIDE.md
"""

import warnings
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional

from BFHTW.utils.logs import get_logger

L = get_logger()

def join_mapping_files(base_dir: Optional[Path | None] = None):
    """
    DEPRECATED: Join PMC mapping files.
    
    This function is deprecated. Use PMCDataSource._get_merged_data() instead.
    """
    warnings.warn(
        "join_mapping_files is deprecated. Use PMCDataSource._get_merged_data() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
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