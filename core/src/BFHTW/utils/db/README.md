# Document Registration System

This repository contains a Python module designed for bulk registration of documents into a database. It includes utilities for database connections and CRUD operations, ensuring efficient data handling and logging.

## Contents

- `document_register.py`: This file contains the functionality for bulk-inserting documents into the database while avoiding duplicates.
- `sql_connection_wrapper.py`: This file provides a decorator for managing database connections, ensuring that connections are opened and closed properly.

## Structure

### `document_register.py`

This module defines the `register_documents_bulk` function, which:
- Accepts a list of `Document` objects.
- Checks for existing documents in the database using their `external_id`.
- Inserts new documents into the `documents` table, skipping those that already exist.
- Returns a summary of the operation, indicating how many documents were inserted and how many were skipped.

**Key Functions:**
- `register_documents_bulk(documents: List[Document]) -> str`
  - **Parameters:**  
    - `documents`: A list of `Document` instances to be registered.
  - **Returns:** A string summarizing the insertion results.

### `sql_connection_wrapper.py`

This module provides a decorator `db_connector` that simplifies the process of connecting to a SQLite database. It:
- Establishes a connection to the database located at `data/database.db`.
- Ensures that the connection is closed after the wrapped function is executed.

**Key Functions:**
- `db_connector(func: Callable[..., Any]) -> Callable[..., Any]`
  - **Parameters:**  
    - `func`: The function to be wrapped for database connection management.
  - **Returns:** A new function that manages database connections.

## Usage

To use this module, import the necessary functions and call `register_documents_bulk` with a list of `Document` instances. Ensure that your database is properly set up and accessible at the specified path.

## Logging

Logging is handled through a utility function `get_logger`, which provides insights into the operations performed, including any skipped documents during registration.

## Requirements

- Python 3.x
- SQLite3

Ensure that all dependencies are installed and properly configured to use the functionalities provided in this repository.