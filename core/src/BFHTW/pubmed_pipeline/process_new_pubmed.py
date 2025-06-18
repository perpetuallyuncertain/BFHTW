from BFHTW.utils.crud.crud import CRUD
from BFHTW.models.pubmed_pmc import PMCArticleMetadata
from BFHTW.sources.pubmed_pmc.pmc_article_downloader import FetchPMCFullText
from BFHTW.ingest.ingest_pdf import extraction
from BFHTW.ingest.insert_embeddings import insert_embeddings
from BFHTW.ingest.insert_keywords_db import insert_keywords
from BFHTW.utils.logs import get_logger

import shutil

L = get_logger()

def process_full_text():
    # Step 1: Load unprocessed articles
    new_articles = CRUD.get(
        table='pubmed_matched',
        model=PMCArticleMetadata,
        id_field='pubmed_processed',
        id_value=False
    )

    for article in new_articles[:3]:
        try:
            # Step 2: Download and extract tarball
            downloader = FetchPMCFullText(article)
            pdf_path, tarball_path = downloader.run()
            if not tarball_path or not tarball_path.exists():
                L.error(f"Failed to download tarball for {article.file_path}")
                continue

            if not pdf_path or not pdf_path.exists():
                L.error(f"PDF path invalid or missing: {pdf_path}")
                continue

            # Step 3: Ingest text from XML or PDF
            result = extraction(pdf_path=pdf_path)
            if not result:
                L.error(f"Failed to ingest {pdf_path}")

            # Step 4: Generate keywords.
            keywords = insert_keywords()
            if not keywords:
                L.error("Failed to generate keywords")

            # Step 5: Generate and insert embeddings
            embedding_result = insert_embeddings()

            if not embedding_result:
                L.error("Failed to process embeddings")

            # Step 6: Mark as processed in databse.
            if result:
                CRUD.update(
                    table="pubmed_matched",
                    model=PMCArticleMetadata,
                    id_field="accession_id",
                    id_value=article.accession_id,
                    updates={"pubmed_processed": True}
                )
                L.info(f"Marked {article.accession_id} as processed.")
            else:
                L.warning("Failed to mark as processed due to failures.")

            # Step 6: Clean up temporary files (tarball + extraction dir)
            if tarball_path.exists():
                tarball_path.unlink()
            extract_dir = tarball_path.with_suffix("")  # strip .tar.gz
            if extract_dir.exists() and extract_dir.is_dir():
                shutil.rmtree(extract_dir)
            L.info(f"Cleaned up temp files for {article.accession_id}")

        except Exception as e:
            L.error(f"Unexpected error processing article {article.pmcid}: {e}")
