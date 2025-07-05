# AI Assistants Module

The AI Assistants module provides intelligent text analysis and extraction capabilities for biomedical literature, with specialized focus on hepatoblastoma research. This module combines state-of-the-art language models with domain-specific extraction logic to transform unstructured literature into structured clinical insights.

## Overview

This module integrates multiple AI technologies to provide comprehensive biomedical text analysis:

- **BioBERT Integration**: Biomedical language model for domain-specific understanding
- **OpenAI Services**: Advanced language models for complex reasoning tasks
- **Clinical Extraction**: Structured extraction of treatment outcomes and patient characteristics
- **Named Entity Recognition**: Automated identification of medications, diseases, and clinical markers

## Module Structure

```
ai_assistants/
├── base/                       # Base classes and interfaces
├── external/                   # External AI service integrations
│   └── open_ai/               # OpenAI API integration
├── internal/                   # Internal AI model implementations
│   └── bio_bert/              # BioBERT NER and embeddings
├── system_prompt.txt          # Clinical extraction system prompt
└── README.md                  # This file
```

## Core Components

### Internal AI Models (`internal/`)
- **BioBERT NER**: Named Entity Recognition for biomedical text
- **BioBERT Embeddings**: Vector representations for semantic search
- **Clinical Extractors**: Domain-specific extraction algorithms

### External AI Services (`external/`)
- **OpenAI Integration**: GPT models for advanced text analysis
- **Prompt Engineering**: Optimized prompts for clinical data extraction
- **API Management**: Rate limiting and error handling

### Base Classes (`base/`)
- **Assistant Interface**: Common interface for all AI assistants
- **Processing Pipeline**: Standard workflow for text analysis
- **Result Models**: Structured output formats

## Clinical Data Extraction

The AI assistants are specifically configured to extract structured clinical insights from hepatoblastoma literature:

### Extraction Fields

1. **Clinical Markers and Pathways**
   - Gene expressions and mutations (e.g., CTNNB1, AFP)
   - Molecular pathways (Wnt/β-catenin, mTOR)
   - Biomarkers for prognosis and treatment response

2. **Treatment Regimens**
   - Chemotherapy protocols and drug combinations
   - Treatment outcomes (response rates, survival)
   - Dosage information and administration schedules

3. **Resistance and Refractoriness**
   - Signs of treatment-resistant disease
   - Failed salvage therapy attempts
   - Molecular mechanisms of drug resistance

4. **Alternative Therapies**
   - Immunotherapy approaches
   - Targeted molecular therapies
   - Liver transplantation outcomes
   - Novel treatment combinations

5. **Surgical Outcomes**
   - Resection margins and completeness
   - Post-surgical complications
   - Recurrence patterns and timing

6. **Metastatic Patterns**
   - Sites and timing of metastases
   - Progression patterns
   - Impact on treatment planning

7. **Histological Insights**
   - Tumor subtypes and classifications
   - Immunohistochemical findings
   - Tissue-level biomarkers

8. **Clinical Trial Data**
   - Study design and methodology
   - Patient demographics and selection
   - Trial outcomes and safety data

## Usage Examples

### Basic Clinical Extraction
```python
from BFHTW.ai_assistants.external.open_ai.openai_assistant import OpenAIAssistant

# Initialize OpenAI assistant
assistant = OpenAIAssistant()

# Note: Specific clinical extraction methods would be implemented
# based on your research requirements and system_prompt.txt configuration
```

### Named Entity Recognition

```python
from BFHTW.ai_assistants.internal.bio_bert.biobert_ner import BioBERTNER

# Initialize the NER assistant
ner_assistant = BioBERTNER()

# Extract biomedical entities from text
text = "The patient was treated with metformin for type 2 diabetes."
entities = ner_assistant.run(
    text=text,
    block_id="block_001", 
    doc_id="doc_123"
)

# Access extracted entities
print(f"Diseases: {entities.diseases}")
print(f"Chemicals: {entities.chemicals}")
print(f"Genes: {entities.genes}")
```

### OpenAI Assistant for Structured Analysis

```python
from BFHTW.ai_assistants.external.open_ai.openai_assistant import OpenAIAssistant
from BFHTW.models.bio_medical_entity_block import BiomedicalEntityBlock

# Initialize OpenAI assistant with structured output
assistant = OpenAIAssistant(
    name="Biomedical Analyzer",
    response_model=BiomedicalEntityBlock
)

# Analyze biomedical text with structured output
clinical_text = """
Patient presents with acute myocardial infarction. 
ECG shows ST elevation. Troponin levels elevated.
Treatment with aspirin and clopidogrel initiated.
"""

result, cost = assistant.analyse(clinical_text)
print(f"Analysis cost: ${cost:.4f}")
print(f"Extracted conditions: {result.diseases}")
print(f"Extracted chemicals: {result.chemicals}")
```

### Embedding Generation

```python
from BFHTW.ai_assistants.internal.bio_bert.biobert_embeddings import BioBERTEmbedder

# Initialize the embedding assistant
embedder = BioBERTEmbedder()

# Generate embeddings for biomedical text
text = "BRCA1 gene mutations increase breast cancer risk."
embedding = embedder.run(
    text=text,
    block_id="(uuid)",
    doc_id="(uuid)", 
    page=1
)

# Access the embedding vector
print(f"Embedding dimension: {len(embedding.vector)}")
print(f"Text processed: {embedding.text}")
```

## Output Structure

All extractors return structured Pydantic models for consistency:

## Configuration

### System Prompt
The `system_prompt.txt` file contains the master prompt for clinical extraction, optimized for:
- Accurate identification of patient cases
- Structured data extraction
- Handling of multi-case articles
- Quality validation and filtering

### Model Configuration
- **BioBERT**: Pre-trained on biomedical literature
- **OpenAI**: GPT-4 with biomedical fine-tuning
- **Embedding Dimensions**: 768 (BioBERT), 1536 (OpenAI)
- **Processing Batch Size**: Configurable based on available memory

## Integration Points

The AI assistants integrate seamlessly with other BFHTW components:

- **Data Models**: Direct compatibility with `BiomedicalEntityBlock`
- **Vector Storage**: Automatic embedding insertion into Qdrant
- **Processing Pipelines**: Integrated into document processing workflows
- **Quality Assurance**: Built-in validation and error handling

## Performance Considerations

- **Throughput**: ~50-100 articles/hour depending on complexity
- **Memory Usage**: Optimized for local deployment
- **API Limits**: Built-in rate limiting for external services
- **Caching**: Intelligent caching of model outputs

## Research Applications

This module enables advanced research capabilities:

- **Literature Meta-Analysis**: Automated synthesis across studies
- **Treatment Efficacy Analysis**: Comparative outcome analysis
- **Biomarker Discovery**: Pattern identification across literature
- **Clinical Decision Support**: Evidence-based treatment recommendations

## Contributing

When extending the AI assistants module:

1. **Follow Pydantic Models**: Use structured output formats
2. **Add Comprehensive Logging**: Include detailed processing logs
3. **Implement Error Handling**: Graceful degradation for API failures
4. **Add Tests**: Unit tests for all extraction functions
5. **Update Documentation**: Keep examples and schemas current

---

*Built specifically for hepatoblastoma research but extensible to other biomedical domains.*
