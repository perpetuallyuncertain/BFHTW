import torch
import json
from pydantic import BaseModel
from typing import TypeVar
from transformers import AutoTokenizer, AutoModel, pipeline
from typing import List, Literal
from collections import defaultdict
from pathlib import Path
from core.src.BFHTW.models.keywords import FilterModel

AnyResponseModel = TypeVar('AnyResponseModel', bound=BaseModel)

ROOT_DIR = Path(__file__).resolve().parent.parent

class BERT:
    def __init__(self, model_type: Literal["embeddings", "ner"]):
        """
        Initialize a BioBERT model wrapper.

        Parameters:
        - model_type (Literal["embeddings", "ner"]): 
            Specify the type of BioBERT use-case:
            - 'embeddings' uses the base BioBERT model for vector embeddings.
            - 'ner' loads a NER-finetuned BioBERT for named entity recognition.
        """

        if model_type == "embeddings":
            model_name = "dmis-lab/biobert-base-cased-v1.1"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.eval()
        elif model_type == "ner":
            self.model_name = "d4data/biomedical-ner-all"
            self.pipe = pipeline(
                "token-classification",
                model=self.model_name,
                aggregation_strategy="simple"
            )
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")
        
    def embed_text(self, text: str) -> List[float]:
        '''Generate a vector embedding from the block text.'''
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = self.model(**inputs)
            # Use CLS token representation
            embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
        return embedding

    def extract_keywords(
            self,
            text, 
            label_map_filename: str, 
            block_id: str, 
            doc_id: str
            ) -> FilterModel:

        local_map_path = ROOT_DIR / 'models' / 'bio_bert' / label_map_filename

        with open(local_map_path, 'r') as f:
            label_map = json.load(f)
        
        
        entities = self.pipe(text)
        categories = defaultdict(list)

        for ent in entities:
            key = label_map.get(ent["entity_group"], "other")
            categories[key].append(ent["word"])

        model_fields = FilterModel.model_fields.keys()
        filtered = {k: v for k, v in categories.items() if k in model_fields}
        return FilterModel(
            block_id=block_id,
            doc_id=doc_id,
            embeddings=False,
            model="bert",
            **filtered
        )

    




