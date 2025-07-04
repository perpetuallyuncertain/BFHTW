# Qdrant CRUD Operations

This repository contains Python scripts for managing embeddings in a Qdrant database. It provides functionality to create, read, update, and delete (CRUD) embeddings, as well as check for duplicates within the database. 

## Contents

- **qdrant_crud.py**: A class that encapsulates CRUD operations for managing embeddings in a Qdrant collection.
- **check_duplicates.py**: A script to identify and delete duplicate embeddings based on text content.
- **wsl-apt-packages.txt**: A list of required APT packages for setting up a WSL (Windows Subsystem for Linux) environment to run the scripts.

## Structure

### 1. `qdrant_crud.py`
This file defines the `QdrantCRUD` class, which includes the following methods:
- **`__init__`**: Initializes the Qdrant client and creates a collection if it does not exist.
- **`upsert_embedding`**: Inserts or updates an embedding in the specified collection.
- **`get_similar`**: Retrieves the top K similar embeddings based on a given embedding vector.
- **`delete_by_id`**: Deletes an embedding from the collection using its ID.
- **`query_by_doc_id`**: Queries embeddings by their document ID.
- **`upsert_embeddings_bulk`**: Inserts or updates multiple embeddings in bulk.

### 2. `check_duplicates.py`
This script connects to the Qdrant client and scrolls through all points in the specified collection. It:
- Collects all embeddings and groups them by their text content.
- Identifies duplicates and deletes all but one of each duplicate group.

### 3. `wsl-apt-packages.txt`
This text file lists essential APT packages required for setting up a suitable environment for running the Python scripts on WSL. You can install the packages listed by running:
```bash
sudo apt-get install <package_name>
```

## Usage
To use the scripts:
1. Ensure you have Python and the Qdrant client library installed.
2. Set up your Qdrant server and adjust the connection parameters in the scripts if necessary.
3. Use the `QdrantCRUD` class in your application to manage embeddings.
4. Run `check_duplicates.py` to clean up any duplicate embeddings in your collection.

## Requirements
- Python 3.6+
- Qdrant client library

## License
This project is licensed under the MIT License. See the LICENSE file for details.