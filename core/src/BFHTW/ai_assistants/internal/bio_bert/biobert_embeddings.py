# BFHTW/ai_assistants/internal/biobert/biobert_embedder.py

import torch
from transformers import AutoTokenizer, AutoModel
from typing import List

class BioBERTEmbedder:
    def __init__(self, model_name: str = "dmis-lab/biobert-base-cased-v1.1"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def embed_text(self, text: str) -> List[float]:
        """Generate a vector embedding from input text."""
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = self.model(**inputs)
            # Use CLS token representation
            embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
        return embedding
