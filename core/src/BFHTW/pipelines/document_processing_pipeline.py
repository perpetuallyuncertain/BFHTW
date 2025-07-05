"""
Robust document processing pipeline using the new pipeline framework.

Handles download, parsing, AI analysis, and storage of biomedical documents
with comprehensive validation and error handling.
"""

from typing import Optional, List, Tuple, Union
from pathlib import Path
import shutil
from urllib.parse import urljoin

from BFHTW.pipelines.base_pipeline import BasePipeline, PipelineResult
from BFHTW.pipelines.data_sources import DatabaseSource
from BFHTW.pipelines.validation import create_biomedical_document_validators, CompositeValidator
from BFHTW.models.pubmed_pmc import PMCArticleMetadata
from BFHTW.models.pdf_models import PDFMetadata, PDFBlock
from BFHTW.models.nxml_models import NXMLMetadata, NXMLBlock
from BFHTW.models.bio_medical_entity_block import BiomedicalEntityBlock
from BFHTW.models.qdrant import QdrantEmbeddingModel
from BFHTW.utils.crud.crud import CRUD
from BFHTW.utils.io.tarball_fetcher import TarballFetcher
from BFHTW.utils.pdf.pdf_metadata import PDFReadMeta
from BFHTW.utils.pdf.pdf_block_extractor import PDFBlockExtractor
from BFHTW.utils.nxml.pubmed_parser import PubMedNXMLParser
from BFHTW.ai_assistants.internal.bio_bert.biobert_ner import BioBERTNER
from BFHTW.ai_assistants.internal.bio_bert.biobert_embeddings import BioBERTEmbedder
from BFHTW.utils.qdrant.qdrant_crud import QdrantCRUD
from BFHTW.utils.logs import get_logger
from qdrant_client.models import PointStruct

L = get_logger()

class DocumentProcessingPipeline(BasePipeline[PMCArticleMetadata, dict]):
    """
    Pipeline for processing biomedical documents from download to AI analysis.
    
    Handles:
    - Document download and extraction
    - Format detection (PDF/NXML) 
    - Text extraction and parsing
    - Biomedical NER and embedding generation
    - Vector database storage
    - Comprehensive validation and error handling
    """
    
    def __init__(
        self,
        batch_size: int = 5,
        max_concurrent_downloads: int = 3,
        enable_ai_processing: bool = True,
        enable_embeddings: bool = True,
        temp_dir: Optional[str] = None,
        cleanup_temp_files: bool = True
    ):
        # Create database source for unprocessed articles
        db_source = DatabaseSource(
            table_name='pubmed_fulltext_links',
            query_conditions={'full_text_downloaded': False}
        )
        
        # Create validators for document processing
        # We'll validate different components separately
        validators = []  # Validation will be done per-component
        
        super().__init__(
            name="Document Processing Pipeline",
            source=db_source,
            validators=validators,
            batch_size=batch_size,
            max_retries=2
        )
        
        self.max_concurrent_downloads = max_concurrent_downloads
        self.enable_ai_processing = enable_ai_processing
        self.enable_embeddings = enable_embeddings
        self.cleanup_temp_files = cleanup_temp_files
        
        # Setup temp directory
        base_dir = Path(__file__).parents[1]
        self.temp_root = Path(temp_dir) if temp_dir else base_dir / 'sources' / 'pubmed_pmc' / 'temp'
        self.temp_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize AI models if needed
        self.ner_model = None
        self.embedding_model = None
        self.qdrant_client = None
        
        if self.enable_ai_processing:
            self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Initialize AI models for NER and embedding generation."""
        try:
            if self.enable_ai_processing:
                L.info("Initializing BioBERT NER model...")
                self.ner_model = BioBERTNER()
                
            if self.enable_embeddings:
                L.info("Initializing BioBERT embedding model...")
                self.embedding_model = BioBERTEmbedder()
                
                L.info("Initializing Qdrant client...")
                self.qdrant_client = QdrantCRUD(collection_name='bio_blocks')
                
        except Exception as e:
            L.error(f"Failed to initialize AI models: {str(e)}")
            raise
    
    def process_item(self, item: PMCArticleMetadata) -> Optional[dict]:
        """
        Process a single article through the complete pipeline.
        
        Args:
            item: PMCArticleMetadata for unprocessed article
            
        Returns:
            Dict with processing results or None if failed
        """
        article_id = item.pmcid
        L.info(f"Processing article: {article_id}")
        
        temp_dir = None
        try:
            # Step 1: Setup temporary directory
            temp_dir = self._create_temp_dir(article_id)
            
            # Step 2: Download and extract document
            extracted_path = self._download_and_extract(item, temp_dir)
            if not extracted_path:
                return None
            
            # Step 3: Detect document format and extract content
            doc_info = self._extract_document_content(extracted_path, article_id)
            if not doc_info:
                return None
            
            # Step 4: Store document metadata and blocks
            storage_result = self._store_document_data(doc_info)
            if not storage_result:
                return None
            
            # Step 5: AI processing (NER and embeddings)
            ai_result = None
            if self.enable_ai_processing and doc_info['blocks']:
                ai_result = self._process_with_ai(doc_info['blocks'])
            
            # Step 6: Mark as processed
            self._mark_as_processed(item)
            
            return {
                'article_id': article_id,
                'format': doc_info['format'],
                'blocks_count': len(doc_info['blocks']),
                'ai_processed': ai_result is not None,
                'embedding_count': ai_result.get('embedding_count', 0) if ai_result else 0,
                'ner_count': ai_result.get('ner_count', 0) if ai_result else 0
            }
            
        except Exception as e:
            L.error(f"Failed to process article {article_id}: {str(e)}")
            return None
            
        finally:
            # Cleanup temp directory
            if temp_dir and self.cleanup_temp_files:
                self._cleanup_temp_dir(temp_dir)
    
    def _create_temp_dir(self, article_id: str) -> Path:
        """Create temporary directory for article processing."""
        temp_dir = self.temp_root / f"extract_{article_id}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    def _download_and_extract(self, item: PMCArticleMetadata, temp_dir: Path) -> Optional[Path]:
        """Download and extract article archive."""
        try:
            base_url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/"
            full_url = urljoin(base_url, item.ftp_path)
            
            tarball_filename = Path(item.ftp_path).name
            tarball_path = temp_dir / tarball_filename
            
            L.debug(f"Downloading {full_url} to {tarball_path}")
            
            fetcher = TarballFetcher(self.temp_root.parent)
            downloaded_path = fetcher.download(full_url, target_path=tarball_path)
            
            if not downloaded_path:
                L.error(f"Failed to download {full_url}")
                return None
            
            # Extract contents
            extracted_path = fetcher.extract(downloaded_path, extract_to=temp_dir)
            return extracted_path
            
        except Exception as e:
            L.error(f"Download/extraction failed for {item.pmcid}: {str(e)}")
            return None
    
    def _extract_document_content(self, extracted_path: Path, article_id: str) -> Optional[dict]:
        """Extract content from PDF or NXML document."""
        temp_dir = extracted_path
        
        # Look for PDF or NXML files
        pdf_path = next(temp_dir.rglob("*.pdf"), None)
        nxml_path = next(temp_dir.rglob("*.nxml"), None)
        
        if not pdf_path and not nxml_path:
            L.warning(f"No PDF or NXML found for {article_id}")
            return None
        
        if pdf_path:
            return self._process_pdf(pdf_path, article_id)
        elif nxml_path:
            return self._process_nxml(nxml_path, article_id)
        
        return None
    
    def _process_pdf(self, pdf_path: Path, article_id: str) -> Optional[dict]:
        """Process PDF document."""
        try:
            # Extract metadata
            meta_reader = PDFReadMeta()
            pdf_metadata = meta_reader.extract_metadata(pdf_path=pdf_path)
            
            # Extract text blocks
            block_extractor = PDFBlockExtractor()
            text_blocks = block_extractor.extract_blocks(
                doc_id=pdf_metadata.doc_id, 
                pdf_path=pdf_path
            )
            
            if not text_blocks:
                L.warning(f"No text blocks extracted from PDF: {article_id}")
                return None
            
            # Validate blocks
            validated_blocks = self._validate_blocks(text_blocks, PDFBlock)
            
            return {
                'format': 'pdf',
                'metadata': pdf_metadata,
                'blocks': validated_blocks,
                'original_block_count': len(text_blocks),
                'validated_block_count': len(validated_blocks)
            }
            
        except Exception as e:
            L.error(f"PDF processing failed for {article_id}: {str(e)}")
            return None
    
    def _process_nxml(self, nxml_path: Path, article_id: str) -> Optional[dict]:
        """Process NXML document."""
        try:
            # Parse NXML
            parser = PubMedNXMLParser(nxml_path)
            
            # Extract metadata
            nxml_metadata = parser.get_metadata()
            
            # Extract blocks
            text_blocks = list(parser.extract_blocks())
            
            if not text_blocks:
                L.warning(f"No text blocks extracted from NXML: {article_id}")
                return None
            
            # Validate blocks
            validated_blocks = self._validate_blocks(text_blocks, NXMLBlock)
            
            return {
                'format': 'nxml',
                'metadata': nxml_metadata,
                'blocks': validated_blocks,
                'original_block_count': len(text_blocks),
                'validated_block_count': len(validated_blocks)
            }
            
        except Exception as e:
            L.error(f"NXML processing failed for {article_id}: {str(e)}")
            return None
    
    def _validate_blocks(self, blocks: List, block_model) -> List:
        """Validate extracted blocks using document validators."""
        validators = create_biomedical_document_validators(
            model=block_model,
            required_fields=['block_id', 'doc_id', 'text'],
            strict_schema=False
        )
        
        composite_validator = CompositeValidator(validators, stop_on_first_error=False)
        validated_blocks = []
        
        for block in blocks:
            validation_result = composite_validator.validate(block)
            
            if validation_result.is_valid:
                validated_blocks.append(block)
            else:
                L.warning(f"Block validation failed: {validation_result.errors}")
                # Could choose to include blocks with warnings only
                if not validation_result.errors and validation_result.warnings:
                    validated_blocks.append(block)
        
        return validated_blocks
    
    def _store_document_data(self, doc_info: dict) -> bool:
        """Store document metadata and blocks in database."""
        try:
            format_type = doc_info['format']
            metadata = doc_info['metadata']
            blocks = doc_info['blocks']
            
            # Store metadata
            if format_type == 'pdf':
                table_name = 'pdf_metadata'
                CRUD.insert(
                    table=table_name,
                    model=PDFMetadata,
                    data=metadata
                )
                
                # Store blocks
                CRUD.bulk_insert(
                    table='pdf_blocks',
                    model=PDFBlock,
                    data_list=blocks
                )
                
            elif format_type == 'nxml':
                table_name = 'nxml_metadata'
                CRUD.insert(
                    table=table_name,
                    model=NXMLMetadata,
                    data=metadata
                )
                
                # Store blocks
                CRUD.bulk_insert(
                    table='nxml_blocks',
                    model=NXMLBlock,
                    data_list=blocks
                )
            
            L.info(f"Stored {format_type} metadata and {len(blocks)} blocks")
            return True
            
        except Exception as e:
            L.error(f"Failed to store document data: {str(e)}")
            return False
    
    def _process_with_ai(self, blocks: List) -> Optional[dict]:
        """Process blocks with AI models for NER and embeddings."""
        try:
            ner_results = []
            embeddings = []
            
            # Process each block
            for block in blocks:
                # Named Entity Recognition
                if self.ner_model:
                    try:
                        ner_result = self.ner_model.run(
                            text=block.text,
                            doc_id=block.doc_id,
                            block_id=block.block_id
                        )
                        ner_results.append(ner_result)
                    except Exception as e:
                        L.warning(f"NER failed for block {block.block_id}: {str(e)}")
                
                # Embedding generation
                if self.embedding_model:
                    try:
                        embedding = self.embedding_model.run(
                            text=block.text,
                            doc_id=block.doc_id,
                            block_id=block.block_id,
                            page=getattr(block, 'page', 1)
                        )
                        embeddings.append(embedding)
                    except Exception as e:
                        L.warning(f"Embedding generation failed for block {block.block_id}: {str(e)}")
            
            # Store NER results
            if ner_results:
                CRUD.bulk_insert(
                    table='bio_blocks',
                    model=BiomedicalEntityBlock,
                    data_list=ner_results
                )
            
            # Store embeddings in Qdrant
            if embeddings and self.qdrant_client:
                points = [
                    PointStruct(
                        id=embedding.block_id,
                        vector=embedding.embedding,
                        payload={
                            "doc_id": embedding.doc_id,
                            "page": embedding.page,
                            "text": embedding.text[:1000],  # Limit text size
                        }
                    )
                    for embedding in embeddings
                ]
                
                self.qdrant_client.upsert_embeddings_bulk(points)
            
            return {
                'ner_count': len(ner_results),
                'embedding_count': len(embeddings)
            }
            
        except Exception as e:
            L.error(f"AI processing failed: {str(e)}")
            return None
    
    def _mark_as_processed(self, item: PMCArticleMetadata):
        """Mark article as processed in database."""
        try:
            CRUD.update(
                table='pubmed_fulltext_links',
                model=PMCArticleMetadata,
                updates={"full_text_downloaded": True},
                id_field='pmcid',
                id_value=item.pmcid
            )
        except Exception as e:
            L.error(f"Failed to mark article as processed: {str(e)}")
    
    def _cleanup_temp_dir(self, temp_dir: Path):
        """Clean up temporary directory."""
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception as e:
            L.warning(f"Failed to cleanup temp directory {temp_dir}: {str(e)}")
    
    def store_item(self, result: dict) -> bool:
        """Store pipeline result (already handled in process_item)."""
        return result is not None

def run_document_processing_pipeline(
    batch_size: int = 5,
    max_articles: Optional[int] = None,
    enable_ai: bool = True,
    enable_embeddings: bool = True
) -> PipelineResult:
    """
    Execute the document processing pipeline.
    
    Args:
        batch_size: Number of articles to process simultaneously
        max_articles: Maximum articles to process (None for all)
        enable_ai: Whether to run AI processing (NER/embeddings)
        enable_embeddings: Whether to generate embeddings
        
    Returns:
        PipelineResult with execution statistics
    """
    # Create necessary tables
    CRUD.create_table_if_not_exists(
        table='pdf_metadata',
        model=PDFMetadata,
        primary_key='doc_id'
    )
    
    CRUD.create_table_if_not_exists(
        table='pdf_blocks',
        model=PDFBlock,
        primary_key='block_id'
    )
    
    CRUD.create_table_if_not_exists(
        table='bio_blocks',
        model=BiomedicalEntityBlock,
        primary_key='block_id'
    )
    
    # Initialize and run pipeline
    pipeline = DocumentProcessingPipeline(
        batch_size=batch_size,
        enable_ai_processing=enable_ai,
        enable_embeddings=enable_embeddings
    )
    
    result = pipeline.run()
    
    # Log summary
    if result.status.value == "success":
        L.info(f"Document processing pipeline completed successfully:")
        L.info(f"  - Processed: {result.processed_count} articles")
        L.info(f"  - Execution time: {result.execution_time:.2f} seconds")
    else:
        L.error(f"Document processing pipeline completed with errors:")
        L.error(f"  - Processed: {result.processed_count} articles")
        L.error(f"  - Failed: {result.failed_count} articles")
    
    return result

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run document processing pipeline")
    parser.add_argument("--batch-size", type=int, default=5, help="Batch size")
    parser.add_argument("--max-articles", type=int, help="Maximum articles to process")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI processing")
    parser.add_argument("--no-embeddings", action="store_true", help="Disable embeddings")
    
    args = parser.parse_args()
    
    result = run_document_processing_pipeline(
        batch_size=args.batch_size,
        max_articles=args.max_articles,
        enable_ai=not args.no_ai,
        enable_embeddings=not args.no_embeddings
    )
    
    exit(0 if result.status.value == "success" else 1)
