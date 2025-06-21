#!/bin/bash -xe

set -e

# === Setup Paths ===
SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR/../../../../..")"
STORAGE_DIR="$PROJECT_ROOT/core/qdrant_storage"

echo "Creating storage directory for Qdrant at: $STORAGE_DIR"
mkdir -p "$STORAGE_DIR"

# === Start Qdrant ===
echo "Starting Qdrant container with docker run..."
docker run -d \
  --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v "${STORAGE_DIR}:/qdrant/storage" \
  qdrant/qdrant

# === Wait and Check Health ===
echo "Waiting for Qdrant to respond..."
sleep 5

echo "Checking Qdrant health..."
if curl -s http://localhost:6333 | grep -q '"status":"ok"'; then
    echo "Qdrant is running and healthy at http://localhost:6333"
else
    echo "Qdrant did not respond. Showing logs:"
    docker logs qdrant
    exit 1
fi
