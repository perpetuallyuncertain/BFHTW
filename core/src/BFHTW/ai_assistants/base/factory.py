# ai_assistants/base/factory.py
from BFHTW.ai_assistants.external.openai.openai_embedder import OpenAIEmbedder
from BFHTW.ai_assistants.internal.biobert.biobert_embedder import BioBERTEmbedder

def get_assistant(model_name: str, task: str):
    if model_name == "openai":
        return OpenAIEmbedder(task)
    elif model_name == "biobert":
        return BioBERTEmbedder(task)
    else:
        raise ValueError(f"Unknown model: {model_name}")
