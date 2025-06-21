# BFHTW/ai_assistants/internal/biobert/biobert_ner.py

import json
from collections import defaultdict
from pathlib import Path
from transformers import AutoTokenizer
from BFHTW.models.bio_medical_entity_block import BiomedicalEntityBlock
from BFHTW.ai_assistants.base.base_local_assistant import BaseLocalAssistant

DEFAULT_LABEL_MAP = Path(__file__).parent / 'label_map.json'

MAX_TOKENS = 512

class BioBERTNER(BaseLocalAssistant[BiomedicalEntityBlock]):
    def __init__(self, model_name: str = "d4data/biomedical-ner-all", label_map_path: Path = DEFAULT_LABEL_MAP):
        super().__init__(
            name="BioBERT-NER",
            model_name=model_name,
            pipeline_type="token-classification",
            response_model=BiomedicalEntityBlock,
            aggregation_strategy="simple"
        )
        self.label_map = json.load(label_map_path.open())
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def _chunk_text(self, text: str, max_tokens: int = MAX_TOKENS) -> list[str]:
        tokens = self.tokenizer.tokenize(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk = self.tokenizer.convert_tokens_to_string(tokens[start:end])
            chunks.append(chunk)
            start = end
        return chunks

    def run(self, text: str, *, block_id: str, doc_id: str) -> BiomedicalEntityBlock: # type: ignore[override]
        entities = self.pipe(text)
        categories = defaultdict(list)

        for ent in entities:
            label = ent.get("entity_group")
            value = ent.get("word")
            key = self.label_map.get(label, "other")
            categories[key].append(value)

        valid_fields = BiomedicalEntityBlock.model_fields.keys()
        filtered = {k: v for k, v in categories.items() if k in valid_fields}

        return BiomedicalEntityBlock(
            block_id=block_id,
            doc_id=doc_id,
            embeddings=False,
            model="bert",
            **filtered
        )