# BFHTW/ai_assistants/internal/biobert/biobert_embedder.py

import torch
from transformers import AutoTokenizer, AutoModel
from BFHTW.models.qdrant import QdrantEmbeddingModel
from BFHTW.ai_assistants.base.base_local_assistant import BaseLocalAssistant

MAX_TOKENS = 512

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

    def run(self, text: str, *, block_id: str, doc_id: str, page: int) -> QdrantEmbeddingModel:  # type: ignore[override]
        chunks = self._chunk_text(text)
        all_embeddings = []

        for chunk in chunks:
            inputs = self.tokenizer(
                chunk,
                return_tensors="pt",
                truncation=True,
                max_length=MAX_TOKENS,
                padding="max_length"
            )
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Mean pooling over token embeddings
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
                all_embeddings.append(embedding)

        # Average across all chunks
        if len(all_embeddings) > 1:
            embedding_tensor = torch.tensor(all_embeddings)
            final_embedding = embedding_tensor.mean(dim=0).tolist()
        else:
            final_embedding = all_embeddings[0]

        return QdrantEmbeddingModel(
            doc_id=doc_id,
            block_id=block_id,
            page=page,
            text=text,
            embedding=final_embedding
        )

