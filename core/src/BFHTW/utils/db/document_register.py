from BFHTW.utils.crud.crud import CRUD
from BFHTW.models.document_main import Document
from datetime import datetime
from BFHTW.utils.logs import get_logger
from typing import List

L = get_logger()

def register_documents_bulk(documents: List[Document]) -> str:
    """
    Bulk-inserts new documents into the 'documents' table.
    Skips any documents with external_id values that already exist.

    Returns:
        A summary string of how many records were inserted vs skipped.
    """
    if not documents:
        return "No documents to register."

    # Fetch all existing external_ids in one query
    existing_docs = CRUD.get(
        table='documents',
        model=Document,
        ALL=True
    )
    existing_ids = {doc.external_id for doc in existing_docs}

    to_insert = []
    skipped = 0

    for doc in documents:
        if doc.external_id in existing_ids:
            L.info(f"[SKIP] Document {doc.external_id} already exists.")
            skipped += 1
            continue

        doc.retrieved_at = doc.retrieved_at or datetime.now().isoformat()
        to_insert.append(doc)

    if to_insert:
        CRUD.bulk_insert(
            table='documents',
            model=Document,
            data_list=to_insert
        )

    return f"Inserted {len(to_insert)} new documents. Skipped {skipped} duplicates."
