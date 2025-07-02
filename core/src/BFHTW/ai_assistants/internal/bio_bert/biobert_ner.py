"""
Module: biobert_ner.py
Purpose:
    Provides a BioBERT-based assistant for biomedical named entity recognition (NER).
    Converts unstructured text into structured entities using a token classification pipeline.

    The assistant uses a predefined label map to convert model output into categories
    defined in the BiomedicalEntityBlock schema.

Classes:
    BioBERTNER: A local assistant that extracts biomedical entities using a BioBERT-based
                token classification model and organizes them by entity type.
"""

import json
from json import JSONDecodeError
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any
from transformers import AutoTokenizer
from BFHTW.models.bio_medical_entity_block import BiomedicalEntityBlock
from BFHTW.ai_assistants.base.base_local_assistant import BaseLocalAssistant
from BFHTW.utils.logs import get_logger

L = get_logger()

DEFAULT_LABEL_MAP = Path(__file__).parent / 'label_map.json'

MAX_TOKENS = 512

class BioBERTNER(BaseLocalAssistant[BiomedicalEntityBlock]):
    """
    A local assistant that uses a BioBERT NER model to extract biomedical entities
    from free text and map them into a structured format using a label map.

    Attributes:
        label_map (dict): Mapping from model-predicted labels to target entity categories.
        tokenizer: Hugging Face tokenizer for chunking and token boundary alignment.
    """

    def __init__(self, model_name: str = "d4data/biomedical-ner-all", label_map_path: Path = DEFAULT_LABEL_MAP):
        """
        Initialize the BioBERTNER assistant.

        Args:
            model_name (str): Hugging Face model identifier. Defaults to a multi-class biomedical NER model.
            label_map_path (Path): Path to the JSON file mapping NER labels to target schema fields.
        """
        super().__init__(
            name="BioBERT-NER",
            model_name=model_name,
            pipeline_type="token-classification",
            response_model=BiomedicalEntityBlock,
            aggregation_strategy="simple",
            return_all_scores=False
        )
        try:
            with label_map_path.open() as f:
                self.label_map = json.load(f)
        except (OSError, JSONDecodeError) as e:
            L.error(f"Failed to load label map from {label_map_path}: {e}")
            raise RuntimeError("NER label map is required but failed to load.") from e

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def _chunk_text(self, text: str, max_tokens: int = MAX_TOKENS) -> list[str]:
        """
        Splits long text into token-aligned chunks within the model's max token limit.

        Args:
            text (str): The input text to split.
            max_tokens (int): Max token count per chunk.

        Returns:
            list[str]: List of text chunks for sequential processing.
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

    def _run_pipeline(self, text: str) -> List[Dict[str, Any]]:
        """
        Wrapper for self.pipe to ensure output is a list of NER dictionaries.

        Args:
            text (str): Input text for NER.

        Returns:
            List[Dict[str, Any]]: Structured NER output.

        Raises:
            RuntimeError: If output format is unexpected.
        """
        result = self.pipe(text)
        if not isinstance(result, list) or not all(isinstance(e, dict) for e in result):
            raise RuntimeError("Unexpected output from HuggingFace NER pipeline")
        return result

    def run(self, text: str, *, block_id: str, doc_id: str) -> BiomedicalEntityBlock:  # type: ignore[override]
        """
        Run NER on input text and return extracted entities in structured form.

        Args:
            text (str): Raw biomedical text.
            block_id (str): Unique identifier for the text block.
            doc_id (str): Identifier for the source document.

        Returns:
            BiomedicalEntityBlock: Structured representation of the extracted entities.
        """
        chunks = self._chunk_text(text)
        categories = defaultdict(list)

        for chunk in chunks:
            entities = self._run_pipeline(chunk)
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
