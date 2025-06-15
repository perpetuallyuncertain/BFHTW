from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue
from typing import List

class QdrantCRUD:
    def __init__(self, collection_name: str, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name

        if not self.client.collection_exists(collection_name):
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )

    def upsert_embedding(self, block_id: str, doc_id: str, embedding: List[float], payload: dict):
        point = PointStruct(
            id=block_id,
            vector=embedding,
            payload={"doc_id": doc_id, **payload}
        )
        self.client.upsert(collection_name=self.collection_name, points=[point])

    def get_similar(self, embedding: List[float], top_k: int = 5):
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=top_k
        )

    def delete_by_id(self, block_id: str):
        self.client.delete(collection_name=self.collection_name, points_selector=[block_id])

    def query_by_doc_id(self, doc_id: str):
        return self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
            ),
            limit=100
        )
    
    def upsert_embeddings_bulk(self, points: List[PointStruct]):
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
