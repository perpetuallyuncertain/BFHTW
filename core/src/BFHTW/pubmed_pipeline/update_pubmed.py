from BFHTW.models.pubmed_pmc import PMCArticleMetadata
from BFHTW.utils.crud.crud import CRUD
from .BFHTW.sources.pubmed_pmc.fetch.fetch_xml_paths import FetchXML
from BFHTW.utils.logs import get_logger

L = get_logger()

def update_pubmed():
    # Step 1: Run search + join
    fetcher = FetchXML()
    articles_df = fetcher.match_pmcids_to_ftp_paths()

    if articles_df.empty:
        L.warning("No articles matched. Skipping database update.")
        return
    
    column_mapping = {
    "File": "file_path",
    "Accession ID": "accession_id",
    "PMID_x": "pmid_source",
    "License": "license",
    "PMCID": "pmcid",
    "PMID_y": "pmid_mapped"
    }
    articles_df = articles_df.rename(columns=column_mapping)

    # Step 2: Convert to list of Pydantic model instances
    try:
        articles = [PMCArticleMetadata(**row) for row in articles_df.to_dict(orient="records")]
    except Exception as e:
        L.error("Failed to convert articles to PMCArticleMetadata model instances.", exc_info=True)
        return

    # Step 3: Create table if needed
    try:
        CRUD.create_table_if_not_exists(
            table='pubmed_matched',
            model=PMCArticleMetadata,
            primary_key='accession_id'  # NOTE: use Pydantic field name, not alias
        )
    except Exception as e:
        L.error("Error creating pubmed_matched table.", exc_info=True)
        return

    # Step 4: Bulk insert
    try:
        result_msg = CRUD.bulk_insert(
            table='pubmed_matched',
            model=PMCArticleMetadata,
            data_list=articles
        )
        L.info(result_msg)
    except Exception as e:
        L.error("Bulk insert into pubmed_matched failed.", exc_info=True)