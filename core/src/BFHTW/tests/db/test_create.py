import pytest
from pathlib import Path
import json

from BFHTW.utils.crud.crud import CRUD
from BFHTW.models.articles.pydantic import PDFMetadata

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

@pytest.mark.unit
def test_create_pdf_metadata():
    table = "pdf_metadata"
    model = PDFMetadata

    with open(ROOT_DIR / "test_data" / "test_metadata.json", "r") as f:
        data = model(**json.load(f))
    
    CRUD.create_table_if_not_exists(table, model, primary_key="doc_id")

    result = CRUD.insert(table, model, data)
    
    assert result.doc_id == data.doc_id
