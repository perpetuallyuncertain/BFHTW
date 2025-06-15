from BFHTW.models.bio_bert.pydantic import FilterModel
from BFHTW.models.articles.pydantic import BaseModel, BlockData
from BFHTW.models.qdrant.pydantic import QdrantEmbeddingModel
from BFHTW.utils.logs import get_logger
from BFHTW.utils.db.get_unprocessed import get_unprocessed_blocks
from BFHTW.utils.db.handler import db_connector
from BFHTW.ai_assistants.bert_assistant import BERT
#from BFHTW.utils.qdrant.qdrant_crud import upsert_embedding

import pandas as pd
from typing import Type, Optional, TypeVar, Literal

L = get_logger()

AnyResponseModel = TypeVar("ResponseModel", bound=BaseModel)

"""
Initialize the NLPProcessor with a specific table and model type.

Parameters:
- table (str): The name of the database table to process.
- model (AnyResponseModel): The Pydantic model to use for data validation.
"""
class nlp_processor:
    def __init__(
        self,
        source_table: str,
        save_model: Type[AnyResponseModel] = None,
        assistant: str = 'BERT',
        nlp_model: Literal["embeddings", "ner"] = None,
        label_map_filename: Optional[str] = 'label_map.json'
    ):
        self.source_table = source_table
        self.save_model = save_model
        self.label_map_filename = label_map_filename
        self.nlp_model = nlp_model

        marker = "embeddings" if nlp_model == "embeddings" else "processed"

        if nlp_model == "embeddings":
            save_model = QdrantEmbeddingModel
        elif nlp_model == "ner":
            save_model = BlockData

            self.data = get_unprocessed_blocks(
                table=source_table,
                model=save_model,
                marker=marker
            )

        ASSISTANT_CLASSES = {
            "BERT": BERT,
        }

        if assistant.upper() not in ASSISTANT_CLASSES:
            raise ValueError(f"Unsupported assistant: {assistant}")

        self.assistant_instance = ASSISTANT_CLASSES[assistant.upper()](nlp_model)

        self._results = None
        self._embeddings = None

        if nlp_model == 'ner':
            self._results = self.ner()
        elif nlp_model == 'embeddings':
            self._embeddings = self.get_embeddings()

    def ner(self) -> list[FilterModel]:
        results: list[FilterModel] = []
        for row in self.data.itertuples(index=False):
            try:
                keyword_model = self.assistant_instance.extract_keywords(
                    text=row.text,
                    label_map_filename=self.label_map_filename,
                    block_id=row.block_id,
                    doc_id=row.doc_id
                )
                results.append(keyword_model)
            except Exception as e:
                L.error(f"Keyword extraction failed for block_id={row.block_id}: {e}")
        return results

    def get_embeddings(self) -> list[QdrantEmbeddingModel]:
        @db_connector
        def get_unprocessed_blocks_with_page(conn, table='keywords', marker='embeddings'):
            sql = f"""
                SELECT k.*, b.page, b.text
                FROM {table} k
                JOIN pdf_blocks b ON k.block_id = b.block_id
                WHERE k.{marker} = 0
            """
            return pd.read_sql_query(sql, conn)

        data = get_unprocessed_blocks_with_page(table=self.source_table)
        embeddings: list[QdrantEmbeddingModel] = []
        for row in data.itertuples(index=False):
            try:
                vector = self.assistant_instance.embed_text(text=row.text)
                embedding = QdrantEmbeddingModel(
                    doc_id=row.doc_id,
                    block_id=row.block_id,
                    page=row.page,
                    text=row.text,
                    embedding=vector
                )
                embeddings.append(embedding)
            except Exception as e:
                L.error(f"Embedding generation failed for block_id={row.block_id}: {e}")
        return embeddings

    @property
    def output(self) -> list[BaseModel]:
        """
        Returns the relevant output based on the selected NLP model.
        For 'ner', returns list[FilterModel]; for 'embeddings', list[QdrantEmbeddingModel].
        """
        return self._results or self._embeddings
