# README.md

## Project Overview

This project is designed to extract structured, case-level insights from biomedical literature specifically related to hepatoblastoma. The focus is on refractory or advanced presentations of the disease, enabling clinical researchers and data scientists to filter, aggregate, and compare patient cases and studies effectively.

## Purpose

The main objective of this codebase is to provide a systematic approach to gather critical data from clinical articles, which can be utilized for further research and analysis in the field of oncology, particularly concerning hepatoblastoma treatment outcomes and patient characteristics.

## Contents

The folder contains the following key components:

- **system_prompt.txt**: This file describes the scope of extraction, the specific fields of interest, and the structure of the output data model that should be adhered to when processing articles.

- **Python Code Files**: (Assumed to be present based on the description)
  - These files will likely include the implementation of the data extraction logic, data models, and any necessary utilities for processing the articles.

## Data Extraction Scope

The extraction process focuses on the following fields:

1. **Clinical Markers and Pathways**: Information on gene expressions, mutations, and molecular pathways.
2. **Chemotherapy Regimens**: Details on drugs used and treatment outcomes.
3. **Refractoriness or Resistance**: Insights into signs of refractory disease and mechanisms of resistance.
4. **Alternative or Adjunct Therapies**: Information on non-standard treatments and trial phases.
5. **Surgical Outcomes and Relapse**: Data regarding surgical margins and recurrence.
6. **Metastatic Patterns**: Details about metastasis sites and timing.
7. **Cellular or Histological Insights**: Findings related to histological subtypes and biomarkers.
8. **Trial or Case Metadata**: Metadata regarding study types and patient demographics.
9. **Additional Noteworthy Findings**: Any unique observations from the studies.

## Output Structure

The output follows a Python model structure using Pydantic for validation. The top-level output is defined as:

```python
class ArticleCases(BaseModel):
    cases: List[CaseInsights]
```

Each `CaseInsights` object captures individual patient data based on the specified fields, ensuring that only explicitly stated information from the articles is included.

## Usage

This codebase is intended for use by:
- Clinical researchers looking to gather insights from literature.
- Data scientists who require structured data for analysis.
- Oncology treatment modelers developing treatment strategies based on real-world data.

## Conclusion

This project aims to facilitate the extraction of valuable clinical insights from literature on hepatoblastoma, contributing to improved understanding and treatment of this complex disease.