"""
Comprehensive validation framework for biomedical data processing pipelines.

Provides validators for data quality, content integrity, schema compliance,
and domain-specific biomedical validation rules.
"""

from typing import List, Dict, Any, Optional, Type, Union
from pydantic import BaseModel, ValidationError
import re
from datetime import datetime
from pathlib import Path
import json

from BFHTW.pipelines.base_pipeline import DataValidator, ValidationResult
from BFHTW.utils.logs import get_logger

L = get_logger()

# Cache for BioBERT vocabulary to avoid repeated loading
_biobert_vocab_cache = None

class SchemaValidator(DataValidator):
    """Validates data against Pydantic model schemas."""
    
    def __init__(self, model: Type[BaseModel], strict: bool = True):
        self.model = model
        self.strict = strict
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate data against the specified Pydantic model."""
        try:
            if isinstance(data, dict):
                self.model(**data)
            elif hasattr(data, 'model_dump'):
                # Already a Pydantic model, validate fields
                self.model(**data.model_dump())
            else:
                self.model.model_validate(data)
            
            return ValidationResult(is_valid=True, errors=[], warnings=[])
            
        except ValidationError as e:
            errors = []
            warnings = []
            
            for error in e.errors():
                error_msg = f"Field '{'.'.join(str(loc) for loc in error['loc'])}': {error['msg']}"
                
                # In non-strict mode, some errors become warnings
                if not self.strict and error['type'] in ['missing', 'extra']:
                    warnings.append(error_msg)
                else:
                    errors.append(error_msg)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[]
            )

class BiomedicalContentValidator(DataValidator):
    """Validates biomedical-specific content quality and characteristics."""
    
    def __init__(
        self,
        min_text_length: int = 100,
        max_text_length: int = 50000,
        require_biomedical_terms: bool = True,
        use_biobert_vocab: bool = True,
        biomedical_vocabulary_file: Optional[str] = None
    ):
        self.min_text_length = min_text_length
        self.max_text_length = max_text_length
        self.require_biomedical_terms = require_biomedical_terms
        self.use_biobert_vocab = use_biobert_vocab
        
        # Load biomedical vocabulary
        if self.use_biobert_vocab:
            self.biomedical_vocabulary = self._load_biobert_vocabulary()
        else:
            self.biomedical_vocabulary = self._load_biomedical_vocabulary(biomedical_vocabulary_file)
    
    def _load_biobert_vocabulary(self) -> set:
        """Load biomedical vocabulary from BioBERT tokenizer."""
        global _biobert_vocab_cache
        
        if _biobert_vocab_cache is not None:
            return _biobert_vocab_cache
        
        try:
            from transformers import AutoTokenizer
            
            # Use the same BioBERT model as in the NER pipeline
            model_name = "dmis-lab/biobert-base-cased-v1.1"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Extract vocabulary and filter for biomedical terms
            vocab = tokenizer.get_vocab()
            
            # Filter vocabulary for meaningful biomedical terms
            biomedical_vocab = set()
            
            # Biomedical patterns to identify relevant terms
            biomedical_patterns = [
                r'^[a-z]+oma$',  # tumors: hepatoma, carcinoma, etc.
                r'^[a-z]*cancer$',  # cancers
                r'^[a-z]*therapy$',  # therapies
                r'^[a-z]*treatment$',  # treatments
                r'^[a-z]*osis$',  # conditions: fibrosis, etc.
                r'^[a-z]*itis$',  # inflammations
                r'^[a-z]*pathy$',  # diseases: neuropathy, etc.
                r'^[a-z]*gene$',  # genes
                r'^[a-z]*protein$',  # proteins
                r'.*surgical.*',  # surgical terms
                r'.*clinical.*',  # clinical terms
                r'.*medical.*',  # medical terms
                r'.*diagnostic.*',  # diagnostic terms
                r'.*therapeutic.*',  # therapeutic terms
            ]
            
            # Medical/biomedical keywords to include
            biomedical_keywords = {
                'patient', 'patients', 'treatment', 'therapy', 'clinical', 'medical',
                'disease', 'diagnosis', 'symptoms', 'medication', 'drug', 'cancer',
                'tumor', 'gene', 'protein', 'cell', 'tissue', 'surgery', 'surgical',
                'hepatoblastoma', 'liver', 'pediatric', 'oncology', 'chemotherapy',
                'cisplatin', 'doxorubicin', 'metastasis', 'prognosis', 'biopsy',
                'malignant', 'benign', 'carcinoma', 'sarcoma', 'lymphoma', 'leukemia',
                'radiotherapy', 'immunotherapy', 'pathology', 'histology', 'cytology',
                'pharmaceutical', 'pharmacology', 'therapeutic', 'diagnostic',
                'anesthesia', 'antibiotic', 'antiviral', 'vaccine', 'immunization',
                'syndrome', 'disorder', 'condition', 'chronic', 'acute', 'inflammatory',
                'infection', 'viral', 'bacterial', 'fungal', 'parasitic',
                'cardiovascular', 'pulmonary', 'neurological', 'gastrointestinal',
                'endocrine', 'metabolic', 'genetic', 'hereditary', 'congenital',
                'molecular', 'cellular', 'biochemical', 'physiological', 'anatomical'
            }
            
            # Add all biomedical keywords
            biomedical_vocab.update(biomedical_keywords)
            
            # Filter vocabulary using patterns and common biomedical prefixes/suffixes
            for token in vocab.keys():
                # Skip special tokens and very short tokens
                if token.startswith(('##', '[', '<')) or len(token) < 3:
                    continue
                
                token_lower = token.lower()
                
                # Check against biomedical patterns
                for pattern in biomedical_patterns:
                    if re.match(pattern, token_lower):
                        biomedical_vocab.add(token_lower)
                        break
                
                # Include tokens that contain biomedical roots
                biomedical_roots = [
                    'cardio', 'neuro', 'gastro', 'hepato', 'pulmo', 'nephro',
                    'osteo', 'arthro', 'dermato', 'ophthalmo', 'oto', 'rhino',
                    'endo', 'exo', 'hypo', 'hyper', 'inter', 'intra', 'trans',
                    'anti', 'pro', 'pre', 'post', 'sub', 'super', 'micro', 'macro',
                    'onco', 'patho', 'bio', 'pharmaco', 'toxico', 'immuno',
                    'hemato', 'lympho', 'angio', 'vaso', 'myo', 'adeno', 'cyto'
                ]
                
                for root in biomedical_roots:
                    if root in token_lower and len(token_lower) > 5:
                        biomedical_vocab.add(token_lower)
                        break
            
            # Cache the vocabulary
            _biobert_vocab_cache = biomedical_vocab
            
            L.info(f"Loaded {len(biomedical_vocab)} biomedical terms from BioBERT vocabulary")
            return biomedical_vocab
            
        except Exception as e:
            L.warning(f"Could not load BioBERT vocabulary: {e}")
            # Fallback to default vocabulary
            return self._load_default_vocabulary()
    
    def _load_biomedical_vocabulary(self, vocab_file: Optional[str]) -> set:
        """Load biomedical vocabulary from file (fallback method)."""
        if vocab_file and Path(vocab_file).exists():
            try:
                with open(vocab_file, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                L.warning(f"Could not load biomedical vocabulary from file: {e}")
        
        return self._load_default_vocabulary()
    
    def _load_default_vocabulary(self) -> set:
        """Load default biomedical vocabulary as fallback."""
        return {
            'patient', 'patients', 'treatment', 'therapy', 'clinical', 'medical',
            'disease', 'diagnosis', 'symptoms', 'medication', 'drug', 'cancer',
            'tumor', 'gene', 'protein', 'cell', 'tissue', 'surgery', 'surgical',
            'hepatoblastoma', 'liver', 'pediatric', 'oncology', 'chemotherapy',
            'cisplatin', 'doxorubicin', 'metastasis', 'prognosis', 'biopsy',
            'malignant', 'benign', 'carcinoma', 'sarcoma', 'lymphoma', 'leukemia',
            'radiotherapy', 'immunotherapy', 'pathology', 'histology', 'cytology',
            'pharmaceutical', 'pharmacology', 'therapeutic', 'diagnostic',
            'anesthesia', 'antibiotic', 'antiviral', 'vaccine', 'immunization',
            'syndrome', 'disorder', 'condition', 'chronic', 'acute', 'inflammatory',
            'infection', 'viral', 'bacterial', 'fungal', 'parasitic'
        }
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate biomedical content characteristics."""
        errors = []
        warnings = []
        biomedical_score = 0.0
        
        # Extract text content
        text_content = self._extract_text(data)
        
        if not text_content:
            errors.append("No text content found for validation")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Length validation
        text_length = len(text_content.strip())
        if text_length < self.min_text_length:
            errors.append(f"Text too short: {text_length} < {self.min_text_length} characters")
        elif text_length > self.max_text_length:
            warnings.append(f"Text very long: {text_length} > {self.max_text_length} characters")
        
        # Character encoding validation
        if not text_content.isprintable():
            non_printable = sum(1 for c in text_content if not c.isprintable() and c not in '\n\r\t')
            if non_printable > text_length * 0.1:  # More than 10% non-printable
                warnings.append(f"High non-printable character count: {non_printable}")
        
        # Biomedical content validation
        if self.require_biomedical_terms:
            biomedical_score = self._calculate_biomedical_score(text_content)
            if biomedical_score < 0.001:  # Very low biomedical term frequency
                warnings.append(f"Low biomedical content score: {biomedical_score:.4f}")
            elif biomedical_score > 0.05:  # Good biomedical content
                L.debug(f"High biomedical content score: {biomedical_score:.4f}")
        
        # Language detection (basic)
        if self._detect_non_english_content(text_content):
            warnings.append("Possible non-English content detected")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=biomedical_score if self.require_biomedical_terms else None
        )
    
    def _extract_text(self, data: Any) -> str:
        """Extract text content from various data formats."""
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            # Try common text fields
            for field in ['text', 'content', 'abstract', 'body', 'title']:
                if field in data and data[field]:
                    return str(data[field])
        elif hasattr(data, 'text'):
            return str(data.text)
        elif hasattr(data, 'content'):
            return str(data.content)
        
        return ""
    
    def _calculate_biomedical_score(self, text: str) -> float:
        """Calculate biomedical relevance score based on vocabulary overlap."""
        if not text or not self.biomedical_vocabulary:
            return 0.0
        
        # Tokenize text (simple word splitting)
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        # Count biomedical terms
        biomedical_count = sum(1 for word in words if word in self.biomedical_vocabulary)
        
        return biomedical_count / len(words)
    
    def _detect_non_english_content(self, text: str) -> bool:
        """Basic non-English content detection."""
        # Count non-ASCII characters
        non_ascii = sum(1 for c in text if ord(c) > 127)
        return non_ascii > len(text) * 0.1  # More than 10% non-ASCII

class MetadataCompletenessValidator(DataValidator):
    """Validates metadata completeness and required fields."""
    
    def __init__(
        self,
        required_fields: List[str],
        recommended_fields: Optional[List[str]] = None,
        field_patterns: Optional[Dict[str, str]] = None
    ):
        self.required_fields = required_fields
        self.recommended_fields = recommended_fields or []
        self.field_patterns = field_patterns or {}
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate metadata completeness."""
        errors = []
        warnings = []
        
        if isinstance(data, dict):
            data_dict = data
        elif hasattr(data, 'model_dump'):
            data_dict = data.model_dump()
        else:
            errors.append("Data format not supported for metadata validation")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check required fields
        for field in self.required_fields:
            if field not in data_dict or not data_dict[field]:
                errors.append(f"Missing required field: {field}")
        
        # Check recommended fields
        for field in self.recommended_fields:
            if field not in data_dict or not data_dict[field]:
                warnings.append(f"Missing recommended field: {field}")
        
        # Validate field patterns
        for field, pattern in self.field_patterns.items():
            if field in data_dict and data_dict[field]:
                if not re.match(pattern, str(data_dict[field])):
                    errors.append(f"Field '{field}' does not match required pattern: {pattern}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

class ForeignKeyValidator(DataValidator):
    """Validates foreign key relationships and referential integrity."""
    
    def __init__(
        self,
        foreign_keys: Dict[str, str],  # field_name -> table_name
        allow_missing: bool = False
    ):
        self.foreign_keys = foreign_keys
        self.allow_missing = allow_missing
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate foreign key relationships."""
        errors = []
        warnings = []
        
        if isinstance(data, dict):
            data_dict = data
        elif hasattr(data, 'model_dump'):
            data_dict = data.model_dump()
        else:
            errors.append("Data format not supported for foreign key validation")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        from BFHTW.utils.crud.crud import CRUD
        
        for field_name, table_name in self.foreign_keys.items():
            if field_name not in data_dict:
                if not self.allow_missing:
                    errors.append(f"Foreign key field missing: {field_name}")
                continue
            
            foreign_key_value = data_dict[field_name]
            if not foreign_key_value:
                if not self.allow_missing:
                    errors.append(f"Foreign key field empty: {field_name}")
                continue
            
            try:
                # Check if referenced record exists
                result = CRUD.get(
                    table=table_name,
                    model=None,  # We just want to check existence
                    id_field=field_name.replace('_id', '_id'),  # Assume standard naming
                    id_value=foreign_key_value
                )
                
                if not result:
                    errors.append(f"Foreign key reference not found: {field_name}={foreign_key_value} in {table_name}")
                    
            except Exception as e:
                warnings.append(f"Could not validate foreign key {field_name}: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

class DuplicateDetectionValidator(DataValidator):
    """Detects potential duplicate entries."""
    
    def __init__(
        self,
        table_name: str,
        unique_fields: List[str],
        similarity_threshold: float = 0.95
    ):
        self.table_name = table_name
        self.unique_fields = unique_fields
        self.similarity_threshold = similarity_threshold
    
    def validate(self, data: Any) -> ValidationResult:
        """Check for potential duplicates."""
        errors = []
        warnings = []
        
        if isinstance(data, dict):
            data_dict = data
        elif hasattr(data, 'model_dump'):
            data_dict = data.model_dump()
        else:
            errors.append("Data format not supported for duplicate detection")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        from BFHTW.utils.crud.crud import CRUD
        
        try:
            # Check exact matches on unique fields
            for field in self.unique_fields:
                if field in data_dict and data_dict[field]:
                    existing = CRUD.get(
                        table=self.table_name,
                        model=None,
                        id_field=field,
                        id_value=data_dict[field]
                    )
                    
                    if existing:
                        errors.append(f"Duplicate found for {field}={data_dict[field]} in {self.table_name}")
            
            # TODO: Implement similarity-based duplicate detection
            # This would require more sophisticated text comparison
            
        except Exception as e:
            warnings.append(f"Could not check for duplicates: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

class CompositeValidator(DataValidator):
    """Combines multiple validators into a single validation step."""
    
    def __init__(self, validators: List[DataValidator], stop_on_first_error: bool = False):
        self.validators = validators
        self.stop_on_first_error = stop_on_first_error
    
    def validate(self, data: Any) -> ValidationResult:
        """Run all validators and combine results."""
        all_errors = []
        all_warnings = []
        scores = []
        
        for validator in self.validators:
            result = validator.validate(data)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            
            if result.score is not None:
                scores.append(result.score)
            
            # Stop on first error if configured
            if self.stop_on_first_error and result.errors:
                break
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            score=sum(scores) / len(scores) if scores else None
        )

# Factory functions for common validator combinations
def create_biomedical_document_validators(
    model: Type[BaseModel],
    required_fields: Optional[List[str]] = None,
    strict_schema: bool = True
) -> List[DataValidator]:
    """Create standard validators for biomedical document processing."""
    validators = []
    
    # Schema validation
    validators.append(SchemaValidator(model, strict=strict_schema))
    
    # Content quality validation
    validators.append(BiomedicalContentValidator(
        min_text_length=50,
        require_biomedical_terms=True
    ))
    
    # Metadata completeness
    if required_fields:
        validators.append(MetadataCompletenessValidator(required_fields))
    
    return validators

def create_metadata_validators(
    model: Type[BaseModel],
    required_fields: List[str],
    foreign_keys: Optional[Dict[str, str]] = None
) -> List[DataValidator]:
    """Create validators for metadata records."""
    validators = []
    
    # Schema validation
    validators.append(SchemaValidator(model, strict=True))
    
    # Metadata completeness
    validators.append(MetadataCompletenessValidator(required_fields))
    
    # Foreign key validation
    if foreign_keys:
        validators.append(ForeignKeyValidator(foreign_keys))
    
    return validators
