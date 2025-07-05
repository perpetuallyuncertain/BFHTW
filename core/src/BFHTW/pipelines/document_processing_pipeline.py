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
from BFHTW.models.document_main import Document
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

class DocumentProcessingPipeline(BasePipeline[Document, dict]):
    """
    Generic pipeline for processing biomedical documents from the documents table.
    
    Works with any document source (PMC, arXiv, local files) and populates
    all downstream tables according to the schema:
    - blocks (text extraction)
    - figures (image extraction) 
    - embeddings (BioBERT vectors)
    - raw_nxml_metadata/raw_pdf_metadata (format-specific data)
    
    Handles:
    - Document download and extraction based on source_db
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
        # Create database source for unprocessed documents from documents table
        db_source = DatabaseSource(
            table_name='documents',
            query_conditions={'processed': False}
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
    
    def process_item(self, item: Document) -> Optional[dict]:
        """
        Process a single document through the complete pipeline.
        
        Args:
            item: Document from documents table
            
        Returns:
            Dict with processing results or None if failed
        """
        article_id = item.external_id
        L.info(f"Processing document: {article_id} from {item.source_db}")
        
        temp_dir = None
        try:
            # Step 1: Setup temporary directory
            temp_dir = self._create_temp_dir(article_id)
            
            # Step 2: Download and extract document (source-agnostic)
            extracted_path = self._download_and_extract(item, temp_dir)
            if not extracted_path:
                return None
            
            # Step 3: Detect document format and extract content
            doc_info = self._extract_document_content(extracted_path, item)
            if not doc_info:
                return None
            
            # Step 4: Store document metadata and blocks
            storage_result = self._store_document_data(doc_info, item)
            if not storage_result:
                return None
            
            # Step 5: AI processing (NER and embeddings)
            ai_result = None
            if self.enable_ai_processing and doc_info['blocks']:
                ai_result = self._process_with_ai(doc_info['blocks'])
            
            # Step 6: Mark as processed
            self._mark_as_processed(item)
            
            return {
                'doc_id': item.doc_id,
                'external_id': article_id,
                'source_db': item.source_db,
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
    
    def _download_pmc_document(self, item: Document, temp_dir: Path) -> Optional[Path]:
        """Download and extract PMC document."""
        try:
            # Extract FTP path from notes field (temporary solution)
            # TODO: Store FTP path in a proper field or lookup table
            if not item.notes or "FTP Path:" not in item.notes:
                L.error(f"No FTP path found for PMC document {item.external_id}")
                return None
            
            ftp_path = item.notes.split("FTP Path: ")[1].split(",")[0].strip()
            if not ftp_path:
                L.error(f"Invalid FTP path for PMC document {item.external_id}")
                return None
                
            base_url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/"
            full_url = urljoin(base_url, ftp_path)
            
            tarball_filename = Path(ftp_path).name
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
            L.error(f"PMC download failed for {item.external_id}: {str(e)}")
            return None
    
    def _download_arxiv_document(self, item: Document, temp_dir: Path) -> Optional[Path]:
        """Download arXiv document (placeholder for future implementation)."""
        L.warning(f"arXiv download not yet implemented for {item.external_id}")
        return None
    
    def _process_local_document(self, item: Document, temp_dir: Path) -> Optional[Path]:
        """Process local document file."""
        if item.source_file and Path(item.source_file).exists():
            return Path(item.source_file)
        L.error(f"Local file not found: {item.source_file}")
        return None
    
    def _download_and_extract(self, item: Document, temp_dir: Path) -> Optional[Path]:
        """Download and extract document based on source database."""
        try:
            if item.source_db.upper() == "PMC":
                return self._download_pmc_document(item, temp_dir)
            elif item.source_db.upper() == "ARXIV":
                return self._download_arxiv_document(item, temp_dir)
            elif item.source_db.upper() == "LOCAL":
                return self._process_local_document(item, temp_dir)
            else:
                L.error(f"Unsupported source database: {item.source_db}")
                return None
                
        except Exception as e:
            L.error(f"Download/extraction failed for {item.external_id}: {str(e)}")
            return None
    
    def _download_pmc_document(self, item: Document, temp_dir: Path) -> Optional[Path]:
        """Download and extract PMC document."""
        try:
            # Extract FTP path from notes field
            if not item.notes or "FTP Path:" not in item.notes:
                L.error(f"No FTP path found for PMC document {item.external_id}")
                return None
            
            ftp_path = item.notes.split("FTP Path: ")[1].split(",")[0].strip()
            if not ftp_path:
                L.error(f"Invalid FTP path for PMC document {item.external_id}")
                return None
                
            base_url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/"
            full_url = urljoin(base_url, ftp_path)
            
            tarball_filename = Path(ftp_path).name
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
            L.error(f"PMC download failed for {item.external_id}: {str(e)}")
            return None
    
    def _download_arxiv_document(self, item: Document, temp_dir: Path) -> Optional[Path]:
        """Download arXiv document (placeholder for future implementation)."""
        L.warning(f"arXiv download not yet implemented for {item.external_id}")
        return None
    
    def _process_local_document(self, item: Document, temp_dir: Path) -> Optional[Path]:
        """Process local document file."""
        try:
            if not item.source_file:
                L.error(f"No source file specified for local document {item.external_id}")
                return None
            
            source_path = Path(item.source_file)
            if not source_path.exists():
                L.error(f"Local file not found: {source_path}")
                return None
            
            # Copy to temp directory for processing
            target_path = temp_dir / source_path.name
            shutil.copy2(source_path, target_path)
            
            return temp_dir
            
        except Exception as e:
            L.error(f"Local file processing failed for {item.external_id}: {str(e)}")
            return None
    
    def _extract_document_content(self, extracted_path: Path, item: Document) -> Optional[dict]:
        """Extract content from PDF or NXML document."""
        temp_dir = extracted_path
        
        # Look for PDF or NXML files
        pdf_path = next(temp_dir.rglob("*.pdf"), None)
        nxml_path = next(temp_dir.rglob("*.nxml"), None)
        
        if not pdf_path and not nxml_path:
            L.warning(f"No PDF or NXML found for {item.external_id}")
            return None
        
        if pdf_path:
            return self._process_pdf(pdf_path, item)
        elif nxml_path:
            return self._process_nxml(nxml_path, item)
        
        return None
    
    def _process_pdf(self, pdf_path: Path, item: Document) -> Optional[dict]:
        """Process PDF document."""
        try:
            # Extract metadata
            meta_reader = PDFReadMeta()
            pdf_metadata = meta_reader.extract_metadata(pdf_path=pdf_path)
            
            if not pdf_metadata:
                L.error(f"Failed to extract PDF metadata for {item.external_id}")
                return None
            
            # Set the document ID to match our Document record
            pdf_metadata.doc_id = item.doc_id
            
            # Extract text blocks
            block_extractor = PDFBlockExtractor()
            text_blocks = block_extractor.extract_blocks(
                doc_id=item.doc_id, 
                pdf_path=pdf_path
            )
            
            if not text_blocks:
                L.warning(f"No text blocks extracted from PDF: {item.external_id}")
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
            L.error(f"PDF processing failed for {item.external_id}: {str(e)}")
            return None
    
    def _process_nxml(self, nxml_path: Path, item: Document) -> Optional[dict]:
        """Process NXML document."""
        try:
            # Parse NXML with proper parameters
            parser = PubMedNXMLParser(
                file_path=str(nxml_path),
                doc_id=item.doc_id,
                source_db=item.source_db
            )
            
            # Extract metadata
            nxml_metadata = parser.get_nxml_metadata()
            
            # Extract blocks
            text_blocks = list(parser.extract_blocks())
            
            if not text_blocks:
                L.warning(f"No text blocks extracted from NXML: {item.external_id}")
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
            L.error(f"NXML processing failed for {item.external_id}: {str(e)}")
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
    
    def _store_document_data(self, doc_info: dict, item: Document) -> bool:
        """Store document metadata and blocks in database according to schema."""
        try:
            format_type = doc_info['format']
            metadata = doc_info['metadata']
            blocks = doc_info['blocks']
            
            # Store format-specific metadata in appropriate tables
            if format_type == 'pdf':
                # Store in raw_pdf_metadata table
                CRUD.insert(
                    table='raw_pdf_metadata',
                    model=PDFMetadata,
                    data=metadata
                )
                
                # Store blocks in blocks table (generic)
                for block in blocks:
                    # Ensure block has correct doc_id
                    block.doc_id = item.doc_id
                
                CRUD.bulk_insert(
                    table='blocks',
                    model=PDFBlock,
                    data_list=blocks
                )
                
            elif format_type == 'nxml':
                # Store in raw_nxml_metadata table
                CRUD.insert(
                    table='raw_nxml_metadata',
                    model=NXMLMetadata,
                    data=metadata
                )
                
                # Store blocks in blocks table (generic)
                for block in blocks:
                    # Ensure block has correct doc_id
                    block.doc_id = item.doc_id
                
                CRUD.bulk_insert(
                    table='blocks',
                    model=NXMLBlock,
                    data_list=blocks
                )
            
            L.info(f"Stored {format_type} metadata and {len(blocks)} blocks for {item.external_id}")
            return True
            
        except Exception as e:
            L.error(f"Failed to store document data for {item.external_id}: {str(e)}")
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
    
    def _mark_as_processed(self, item: Document):
        """Mark document as processed in database."""
        try:
            CRUD.update(
                table='documents',
                model=Document,
                updates={"processed": True},
                id_field='doc_id',
                id_value=item.doc_id
            )
        except Exception as e:
            L.error(f"Failed to mark document as processed: {str(e)}")
    
    def _cleanup_temp_dir(self, temp_dir: Path):
        """Clean up temporary directory."""
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception as e:
            L.warning(f"Failed to cleanup temp directory {temp_dir}: {str(e)}")
    
    def store_item(self, item: dict) -> bool:
        """Store pipeline result (processing is handled in process_item)."""
        return item is not None

def run_document_processing_pipeline(
    batch_size: int = 5,
    max_articles: Optional[int] = None,
    enable_ai: bool = True,
    enable_embeddings: bool = True
) -> PipelineResult:
    """
    Execute the document processing pipeline.
    
    Args:
        batch_size: Number of documents to process simultaneously
        max_articles: Maximum documents to process (None for all)
        enable_ai: Whether to run AI processing (NER/embeddings)
        enable_embeddings: Whether to generate embeddings
        
    Returns:
        PipelineResult with execution statistics
    """
    # Create necessary tables according to schema
    CRUD.create_table_if_not_exists(
        table='documents',
        model=Document,
        primary_key='doc_id'
    )
    
    CRUD.create_table_if_not_exists(
        table='raw_pdf_metadata',
        model=PDFMetadata,
        primary_key='doc_id'
    )
    
    CRUD.create_table_if_not_exists(
        table='raw_nxml_metadata',
        model=NXMLMetadata,
        primary_key='doc_id'
    )
    
    CRUD.create_table_if_not_exists(
        table='blocks',
        model=PDFBlock,  # Use as representative block model
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
        L.info(f"  - Processed: {result.processed_count} documents")
        L.info(f"  - Execution time: {result.execution_time:.2f} seconds")
    else:
        L.error(f"Document processing pipeline completed with errors:")
        L.error(f"  - Processed: {result.processed_count} documents")
        L.error(f"  - Failed: {result.failed_count} documents")
    
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
