"""
Module: biobert_embedder.py
Purpose:
    Provides a BioBERT-based embedding assistant that processes biomedical text into
    dense vector representations using mean pooling over token embeddings.

    This assistant wraps the BioBERT model and integrates with the QdrantEmbeddingModel
    to support storage and retrieval in a vector database (e.g., Qdrant).

Classes:
    BioBERTEmbedder: A local assistant that converts biomedical text into embeddings
                     using BioBERT with automatic chunking and average pooling.
"""

import torch
from transformers import AutoTokenizer, AutoModel
from BFHTW.models.qdrant import QdrantEmbeddingModel
from BFHTW.ai_assistants.base.base_local_assistant import BaseLocalAssistant

MAX_TOKENS = 512

class BioBERTEmbedder(BaseLocalAssistant[QdrantEmbeddingModel]):
    """
    A local assistant that generates vector embeddings from biomedical text using BioBERT.

    This assistant tokenizes input text, chunks it if necessary, passes it through
    BioBERT, and returns a mean-pooled embedding suitable for similarity search.

    Attributes:
        tokenizer: Hugging Face tokenizer loaded from the BioBERT model.
        model: Hugging Face transformer model for BioBERT.
    """

    def __init__(self, model_name: str = "dmis-lab/biobert-base-cased-v1.1"):
        """
        Initialize the BioBERTEmbedder with a specific BioBERT model.

        Args:
            model_name (str): Hugging Face model identifier. Defaults to dmis-lab BioBERT.
        """
        super().__init__(
            name="BioBERT-Embedder",
            model_name=model_name,
            pipeline_type="feature-extraction",
            response_model=QdrantEmbeddingModel,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def _chunk_text(self, text: str, max_tokens: int = MAX_TOKENS) -> list[str]:
        """
        Splits text into chunks of up to max_tokens tokens, preserving token boundaries.

        Args:
            text (str): The input text to be chunked.
            max_tokens (int): Maximum number of tokens per chunk.

        Returns:
            list[str]: A list of text chunks.
        """
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
        """
        Generate an embedding for the given text using BioBERT with optional chunking.

        Args:
            text (str): Raw biomedical text block.
            block_id (str): Unique ID of the text block.
            doc_id (str): ID of the document the block belongs to.
            page (int): Page number of the document the block is from.

        Returns:
            QdrantEmbeddingModel: A structured object containing metadata and final embedding.
        """
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
