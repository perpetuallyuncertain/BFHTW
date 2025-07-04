# BioBERT NER and Embedding Assistant

This repository contains two modules that utilize the BioBERT model for biomedical text processing: one for Named Entity Recognition (NER) and another for generating text embeddings. These modules are designed to assist in extracting structured information from unstructured biomedical text and to convert this text into dense vector representations for further analysis.

## Contents

- **biobert_ner.py**: A module for biomedical named entity recognition using BioBERT.
- **biobert_embeddings.py**: A module for generating embeddings from biomedical text using BioBERT.
- **label_map.json**: A JSON file that maps NER labels to structured entity categories.

## Modules Overview

### 1. biobert_ner.py

This module provides functionality for biomedical named entity recognition (NER). It uses a BioBERT-based token classification pipeline to convert unstructured biomedical text into structured entities according to the BiomedicalEntityBlock schema.

#### Key Features:
- **Class**: `BioBERTNER`
  - Extracts biomedical entities from text and organizes them by entity type.
  - Utilizes a label map to convert model output into predefined categories.

#### Usage:
- Initialize the `BioBERTNER` class with the model name and path to the label map.
- Call the `run` method with the input text to get structured biomedical entities.

### 2. biobert_embeddings.py

This module processes biomedical text into dense vector representations using mean pooling over token embeddings from the BioBERT model. It is integrated with a vector database (e.g., Qdrant) for efficient storage and retrieval.

#### Key Features:
- **Class**: `BioBERTEmbedder`
  - Converts biomedical text into embeddings suitable for similarity search.
  - Automatically chunks long text to fit within the model's token limits.

#### Usage:
- Initialize the `BioBERTEmbedder` class with the model name.
- Call the `run` method with the text and metadata to generate embeddings.

### 3. label_map.json

This JSON file contains mappings from model-predicted labels to target entity categories. It is used by the `BioBERTNER` class to categorize extracted entities properly.

## Structure

```plaintext
/
├── biobert_ner.py
├── biobert_embeddings.py
└── label_map.json
```

## Installation

To use these modules, ensure that you have the required dependencies installed, including the `transformers` library from Hugging Face. You can install it using pip:

```bash
pip install transformers torch
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.