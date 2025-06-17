from BFHTW.functions.nlp.processor import nlp_processor
from BFHTW.utils.qdrant.qdrant_crud import QdrantCRUD
from BFHTW.utils.crud.crud import CRUD
from core.src.BFHTW.models.qdrant.qdrant import QdrantEmbeddingModel
from BFHTW.utils.logs import get_logger

from qdrant_client.models import PointStruct

L = get_logger()

def insert_embeddings(collection_name: str = 'bio_blocks'):
    '''
    needs logic inserted for timer or other trigger
    
    '''
    """
    Generate embeddings and bulk insert them into Qdrant.
    """
    processor = nlp_processor(
        source_table='keywords',
        save_model=QdrantEmbeddingModel,
        assistant='BERT',
        nlp_model='embeddings',
        label_map_filename=None
    )

    embeddings = processor.output

    if not embeddings:
        L.warning("No embeddings found to insert.")
        return

    points = [
    PointStruct(
        id=embedding.block_id,
        vector=embedding.embedding,  # Assuming this is your 768-dim vector
        payload={
            "doc_id": embedding.doc_id,
            "text": embedding.text,
            "page": embedding.page
        }
    )
    for embedding in embeddings  # List[QdrantEmbeddingModel]
    ]

    try:
        qdrant = QdrantCRUD(collection_name=collection_name)
        success = qdrant.client.upsert(
            collection_name=collection_name,
            points=points
        )
        L.info(f"Inserted {len(points)} vectors into Qdrant collection '{collection_name}'")
    except Exception as e:
        L.error(f"Failed to insert data to Qdrant: {e}")

    if success:
        
        try:
            data_list = [(point.id, {"embeddings": True}) for point in points]

            CRUD.bulk_update(
                table='keywords',
                id_field='block_id',
                data_list=data_list
            )
            L.info(f"Updated pdf_blocks with processed tag for {len(data_list)} rows")
            return True
            
        except Exception as e:
            L.error(f"Failed to update pdf_blocks with {e}")


