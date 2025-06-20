from BFHTW.utils.logs import get_logger
from BFHTW.utils.crud.crud import CRUD
from BFHTW.models.pubmed_pmc import PMCArticleMetadata
from BFHTW.utils.io.tarball_fetcher import TarballFetcher
from BFHTW.ai_assistants.internal.bio_bert.biobert_ner import BioBERTNER
from BFHTW.ai_assistants.internal.bio_bert.biobert_embeddings import BioBERTEmbedder
from BFHTW.utils.pdf.pdf_metadata import PDFReadMeta
from BFHTW.utils.pdf.pdf_block_extractor import PDFBlockExtractor
from BFHTW.models.pdf_extraction import PDFMetadata, PDFBlock
from BFHTW.utils.qdrant.qdrant_crud import QdrantCRUD

import shutil
from pathlib import Path
from urllib.parse import urljoin

L = get_logger()

# Step 1: Get next unprocessed path
unprocessed_paths = CRUD.get(
    table='pubmed_fulltext_links',
    model=PMCArticleMetadata,
    id_field='full_text_downloaded',
    id_value=False
)

if not unprocessed_paths:
    L.info("No unprocessed files left.")
    exit()

path_info = unprocessed_paths[0]

base_dir = Path(__file__).parents[2]

# Step 2: Create temp dir (use pmcid for a clean folder name)
temp_root = base_dir / 'sources' / 'pubmed_pmc' / 'temp'
doc_temp_dir = temp_root / f"extract_{path_info.pmcid}"
doc_temp_dir.mkdir(parents=True, exist_ok=True)

# Step 3: Download TAR.GZ
BASE_URL = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/"
full_url = urljoin(BASE_URL, path_info.ftp_path)

tarball_filename = Path(path_info.ftp_path).name  # e.g., "PMC17774.tar.gz"
tarball_file_path = doc_temp_dir / tarball_filename

fetcher = TarballFetcher(base_dir)
tarball_path = fetcher.download(full_url, target_path=tarball_file_path)

# Step 4: Extract contents
extracted_path = fetcher.extract(tarball_path, extract_to=doc_temp_dir)

# Step 5: Locate PDF
pdf_path = next(doc_temp_dir.rglob("*.pdf"), None)
if not pdf_path:
    L.warning(f"No PDF found for {path_info.doc_id} in {tarball_path}")
    shutil.rmtree(doc_temp_dir)
    exit()

# Step 6: Extract metadata
meta_reader = PDFReadMeta()
pdf_metadata = meta_reader.extract_metadata(pdf_path=pdf_path)

if not pdf_metadata:
    raise ValueError("Failed to extract metadata from PDF")

# Step 7: Extract blocks
block_extractor = PDFBlockExtractor()
text_blocks = block_extractor.extract_blocks(doc_id=pdf_metadata.doc_id, pdf_path=pdf_path)

# Step 8: Insert metadata and blocks
CRUD.insert(
    table='pdf_metadata',
    model=PDFMetadata,
    data=pdf_metadata
)

CRUD.bulk_insert(
    table='pdf_blocks',
    model=PDFBlock,
    data_list=text_blocks
)

# Step 9: Named Entity Recognition
ner = BioBERTNER()
keywords = [
    ner.run(text=block.text, doc_id=block.doc_id, block_id=block.block_id)
    for block in text_blocks
]

# Step 10: Embedding generation
embedder = BioBERTEmbedder()
embeddings = [
    embedder.run(text=block.text, doc_id=block.doc_id, block_id=block.block_id, page=block.page)
    for block in text_blocks
]

# Step 11: Save NER and embeddings
if keywords:
    CRUD.bulk_insert(
        table='biobert_ner_results',
        model=type(keywords[0]),
        data_list=keywords
    )

if embeddings:
    qdrant_client = QdrantCRUD()
    qdrant_client.upsert_embeddings_bulk(
        points=[embedding.model_dump() for embedding in embeddings]
    )
    L.info(f"Inserted {len(embeddings)} embeddings into Qdrant for doc {pdf_metadata.doc_id}")


# Step 12: Cleanup
shutil.rmtree(doc_temp_dir)

# Step 13: Mark as processed
CRUD.update(
    table='pubmed_fulltext_links',
    model=PMCArticleMetadata,
    updates={"full_text_downloaded": True},
    id_field='block_id',
    id_value=path_info.block_id
)

L.info(f"Successfully processed and cleaned up {path_info.block_id}")
