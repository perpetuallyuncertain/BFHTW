# BFHTW/ai_assistants/internal/biobert/biobert_ner.py

import json
from collections import defaultdict
from typing import List
from pathlib import Path
from transformers.pipelines import pipeline
from BFHTW.models.bio_medical_entity_block import FilterModel

ROOT_DIR = Path(__file__).resolve().parents[3]  # same depth as before

class BioBERTNER:
    def __init__(self, model_name: str = "d4data/biomedical-ner-all"):
        self.model_name = model_name
        self.pipe = pipeline(
            "token-classification",
            model=self.model_name,
            aggregation_strategy="simple"
        )

    def extract_keywords(
        self,
        text: str,
        label_map_filename: str,
        block_id: str,
        doc_id: str
    ) -> FilterModel:
        label_map_path = ROOT_DIR / 'models' / 'bio_bert' / label_map_filename
        with open(label_map_path, 'r') as f:
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
