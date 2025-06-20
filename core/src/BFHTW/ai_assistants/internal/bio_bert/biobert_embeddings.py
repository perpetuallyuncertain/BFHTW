# BFHTW/ai_assistants/internal/biobert/biobert_embedder.py

import torch
from transformers import AutoTokenizer, AutoModel
from typing import List
from pathlib import Path
from BFHTW.models.qdrant import QdrantEmbeddingModel
from BFHTW.ai_assistants.base.base_local_assistant import BaseLocalAssistant

class BioBERTEmbedder(BaseLocalAssistant[QdrantEmbeddingModel]):
    def __init__(self, model_name: str = "dmis-lab/biobert-base-cased-v1.1"):
        super().__init__(
            name="BioBERT-Embedder",
            model_name=model_name,
            pipeline_type="feature-extraction",
            response_model=QdrantEmbeddingModel,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def run(self, text: str, *, block_id: str, doc_id: str, page: int) -> QdrantEmbeddingModel: # type: ignore[override]
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Mean pooling over tokens
            embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()

        return QdrantEmbeddingModel(
            doc_id=doc_id,
            block_id=block_id,
            page=page,
            text=text,
            embedding=embeddings
        )

