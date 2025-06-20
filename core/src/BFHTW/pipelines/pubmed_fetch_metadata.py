import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import datetime
from BFHTW.utils.crud.crud import CRUD
from BFHTW.utils.logs import get_logger

L = get_logger()

# Step 1: Update reference files:
'''
To fetch Pubmed PMC data, two reference files are required to identify the document ftp addresses to be downloaded.
'''

from BFHTW.sources.pubmed_pmc.fetch.fetch_file_list import FileListFetcher
list_fetcher = FileListFetcher()

latest_file_list: pd.DataFrame = list_fetcher.fetch_new_articles()
'''
This will fetch the latest file list from the ftp server and save it at core/src/BFHTW/sources/pubmed_pmc/data/oa_file_list_{date}.csv
'''

from BFHTW.sources.pubmed_pmc.fetch.fetch_PMCID_mapping import PMCIDMappingFetcher
id_fetcher = PMCIDMappingFetcher()
pmc_ids: pd.DataFrame = id_fetcher.fetch()
'''
This will fetch the latest PMCID mapping file from the ftp server and save it at core/src/BFHTW/sources/pubmed_pmc/data/PMC-ids_{date}.csv
'''

# Step 3: Fetch XML paths to download data

'''
The above uses the pubmed API to fetch matching articles based on the search terms located here: /home/steven/BFHTW/core/src/BFHTW/sources/pubmed_pmc/search_terms.json
Then the returned PMCIDs are compared against the merged files from above to map the XML paths of the relevant files
'''

from BFHTW.sources.pubmed_pmc.fetch.fetch_xml_paths import FetchXML
from BFHTW.models.pubmed_pmc import PMCArticleMetadata
xml_fetch = FetchXML()
article_paths = xml_fetch.match_pmcids_to_ftp_paths()

# Step 5: Save list to SQL

field_map = {
    "File":              "ftp_path",
    "Accession ID":      "accession_id",
    "PMID_x":            "pmid_source",
    "License":           "license_type",
    "PMCID":             "pmcid",
    "PMID_y":            "pmid_mapped"
}

rows = []

for _, row in article_paths.iterrows():
    model_data = {model_field: row[source_field] for source_field, model_field in field_map.items()}
    model_data["full_text_downloaded"] = False
    rows.append(PMCArticleMetadata(**model_data))

# Insert into SQL
CRUD.bulk_insert(
    table='pubmed_fulltext_links',
    model=PMCArticleMetadata,
    data_list=rows
)
L.info(f"Inserted {len(rows)} articles into the table pubmed_fulltext_links")










