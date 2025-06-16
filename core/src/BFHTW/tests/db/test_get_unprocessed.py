import pytest
from typing import TypeVar
import pandas as pd
from BFHTW.utils.db.get_unprocessed import get_unprocessed_blocks
from BFHTW.models.articles.pydantic import BaseModel, BlockData

AnyResponseModel = TypeVar("ResponseModel", bound=BaseModel)

@pytest.mark.unit
def test_get_unprocessed():
        table = input(f"Insert table name: ")
        marker = input(f"Insert marker label: ")

        test_data = get_unprocessed_blocks(
            table = table,
            model = BlockData,
            marker=marker
        )

        assert isinstance(test_data, pd.DataFrame)