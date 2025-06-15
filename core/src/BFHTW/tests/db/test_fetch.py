import pytest
import pandas as pd

from BFHTW.utils.crud.crud import CRUD
from BFHTW.models.articles.pydantic import BlockData

@pytest.mark.dev
def test_fetch():
    table = "pdf_blocks"
    model = BlockData

    raw_data = CRUD.get(
        table=table,
        model=model,
        ALL=True,
    )

    assert raw_data is not None, "No data returned from CRUD.get()"
    assert isinstance(raw_data, list), "Expected list of model instances"

    data = pd.DataFrame([item.model_dump() for item in raw_data])
    assert not data.empty, "DataFrame is empty after conversion"

    # Optional: Check for required columns
    required_cols = ["doc_id", "block_id"]
    for col in required_cols:
        assert col in data.columns, f"Missing column: {col}"


    

