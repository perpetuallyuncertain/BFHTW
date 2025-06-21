from qdrant_client import QdrantClient
from collections import defaultdict
from qdrant_client.models import PointIdsList

# Connect to Qdrant
client = QdrantClient("http://localhost:6333")

collection = "bio_blocks"
scroll_limit = 10000

# Scroll through all points
all_points = []
offset = None

while True:
    response = client.scroll(
        collection_name=collection,
        limit=scroll_limit,
        with_payload=True,
        with_vectors=False,
        offset=offset,
    )
    points, next_offset = response

    all_points.extend(points)

    if next_offset is None:
        break
    offset = next_offset

# Group point IDs by text content
text_map = defaultdict(list)
for pt in all_points:
    text = pt.payload.get("text")
    if text:
        text_map[text].append(pt.id)

# Identify duplicate IDs (keep 1, delete rest)
duplicate_ids = []
for ids in text_map.values():
    if len(ids) > 1:
        duplicate_ids.extend(ids[1:])  # keep the first, delete the rest

print(f"Identified {len(duplicate_ids)} duplicate points to delete.")

client.delete(
    collection_name="bio_blocks",
    points_selector=PointIdsList(points=duplicate_ids),
    wait=True
)