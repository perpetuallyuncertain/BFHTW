import pytest
from BFHTW.functions.nlp.processor import nlp_processor
from core.src.BFHTW.models.keywords import FilterModel
from core.src.BFHTW.models.qdrant.qdrant import QdrantEmbeddingModel

@pytest.mark.unit
def test_nlp_processor():

    source_table = input(f"What is the source table called? ")
    nlp_model = input(f"What nlp function are we testing? ")

    if nlp_model == "ner":
        save_model = FilterModel

        default_label_map = str.lower(input(f"Use default label map? (Y/N)"))
        
        if default_label_map == "y":
            label_map_filename = 'label_map.json'
        else:
            label_map_filename = input(str(f"What is the filename you wish to use? "))

        processor = nlp_processor(
            source_table=source_table,
            save_model=save_model,
            nlp_model=nlp_model,
            label_map_filename=label_map_filename
        )

        assert isinstance(processor._results, list)

    else:
        nlp_model == "embeddings"
        
        processor = nlp_processor(
            source_table='keywords',
            save_model=QdrantEmbeddingModel,
            nlp_model='embeddings'
        )

        assert isinstance(processor._embeddings, list)

   

    