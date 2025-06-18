import pandas as pd
from pandas import DataFrame
from typing import Optional, Type, List, Literal

from BFHTW.models.pdf_metadata import BaseModel
from BFHTW.utils.logs import get_logger
from BFHTW.utils.crud.crud import CRUD

L = get_logger()

def get_unprocessed_blocks(
    table: str,
    model: Type[BaseModel],
    doc_id: Optional[str] = None,
    block_id: Optional[List[str]] = None,
    marker: Optional[Literal["processed", "embeddings"]] = None,
) -> DataFrame:
        
        """
    Retrieve unprocessed blocks from the database based on provided filters.
    
    Parameters:
        table (str): Name of the table to query.
        model (Type[BaseModel]): Pydantic model to use for deserialization.
        doc_id (Optional[str]): Filter results by document ID.
        block_id (Optional[List[str]]): Filter results by block ID(s).
        processed (Optional[bool]): If False, filter by unprocessed rows.
        
    Returns:
        DataFrame: A DataFrame containing the unprocessed blocks.
    """
        
        if block_id:
            id_field = "block_id"
            id_value = block_id
        elif doc_id:
            id_field = "doc_id"
            id_value = doc_id
        elif marker:
            id_field=marker
            id_value=False
        
        records = CRUD.get(
             table = table,
             model = model,
             id_field=id_field,
             id_value=id_value
        )

        unprocessed = pd.DataFrame([r.model_dump() for r in records])

        if unprocessed.empty:
            L.warning(f"No unprocessed blocks found for {id_field}={id_value} in table {table}")
            return pd.DataFrame()
        L.info(f"Found {len(unprocessed)} unprocessed blocks")
        return unprocessed
    