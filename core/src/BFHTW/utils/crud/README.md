# CRUD Operations Module

This module provides a set of CRUD (Create, Read, Update, Delete) operations for interacting with a database using Pydantic models. It includes methods for inserting, retrieving, updating, and deleting records, as well as creating tables and performing bulk operations.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Methods](#methods)
- [Logging](#logging)
- [Contributing](#contributing)

## Installation
To use this module, ensure you have the following dependencies installed:
- `pydantic`
- Database connector library (e.g., SQLite)

You can install them using pip:
```bash
pip install pydantic
```

## Usage
To use the CRUD operations, you will need to define your data models using Pydantic and then call the appropriate methods from the `CRUD` class. Here’s a basic example:

```python
from pydantic import BaseModel
from crud import CRUD

class User(BaseModel):
    id: int
    name: str
    email: str

# Create a table
CRUD.create_table_if_not_exists(conn, 'users', User, primary_key='id')

# Insert a user
user = User(id=1, name='John Doe', email='john@example.com')
CRUD.insert(conn, 'users', User, user)

# Retrieve user
retrieved_user = CRUD.get(conn, 'users', User, id_field='id', id_value=1)
```

## Methods
The following methods are provided in the `CRUD` class:

- `insert(conn, table, model, data)`: Inserts a new record into the specified table.
- `get(conn, table, model, id_field=None, id_value=None, ALL=False)`: Retrieves records from the specified table.
- `update(conn, table, model, updates, id_field=None, id_value=None)`: Updates a record in the specified table.
- `delete(conn, table, id_field, id_value)`: Deletes a record from the specified table.
- `create_table_if_not_exists(conn, table, model, primary_key, unique_fields=None)`: Creates a table if it does not already exist.
- `bulk_insert(conn, table, model, data_list)`: Inserts multiple records into the specified table.
- `bulk_update(conn, table, id_field, data_list, param_style='named')`: Updates multiple records in the specified table.

## Logging
The module uses a logging utility to log messages related to database operations. Ensure that the logging configuration is set up correctly in your application to capture these logs.

## Contributing
Contributions are welcome! If you would like to contribute to this project, please fork the repository and submit a pull request with your changes.

--- 

This README provides a concise overview of the CRUD module, its usage, and methods. Ensure to replace the placeholder text with specific details relevant to your project as necessary.