from typing import Type, List
from pydantic import BaseModel
from typing import Any, Optional, Union, Type, get_origin, get_args, Annotated
import json

from BFHTW.utils.db.sql_connection_wrapper import db_connector
from BFHTW.utils.logs import get_logger

L = get_logger()

class CRUD:

    type_mapping = {
    str: "TEXT",
    int: "INTEGER",
    float: "REAL",
    bool: "BOOLEAN",
}
    @staticmethod
    def _resolve_base_type(py_type):
        if get_origin(py_type) is Annotated:
            return get_args(py_type)[0]
        return py_type

    @staticmethod
    @db_connector
    def insert(
        conn, 
        table: str, 
        model: Type[BaseModel], 
        data: BaseModel
        ):
        
        fields = list(data.model_dump().keys())
        placeholders = ', '.join(['?'] * len(fields))
        columns = ', '.join(fields)
        values = tuple(data.model_dump().values())

        sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
        conn.execute(sql, values)
        return data

    @staticmethod
    @db_connector
    def get(
        conn,
        table: str, 
        model: Type[BaseModel], 
        id_field: Optional[str] = None,
        id_value: Optional[Union[str, int, float, bool]] = None, 
        ALL: bool = False):
        if ALL:
            sql = f"SELECT * FROM {table}"
            rows = conn.execute(sql).fetchall()
        elif id_field and id_value is not None:
            sql = f"SELECT * FROM {table} WHERE {id_field} = ?"
            rows = conn.execute(sql, (id_value,)).fetchall()
        else:
            raise ValueError("Must provide either ALL=True or (id_field + id_value)")

        return [model(**dict(row)) for row in rows] if rows else []

    @staticmethod
    @db_connector
    def update(
        conn, 
        table: str, 
        model: Type[BaseModel],
        updates: dict[str, Any], 
        id_field: Optional[str] = None,
        id_value: Optional[Union[str, int, float, bool]] = None, 
        
        ):
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [id_value]

        sql = f"UPDATE {table} SET {set_clause} WHERE {id_field} = ?"
        conn.execute(sql, values)
        return CRUD.get(table=table, model=model, id_field=id_field, id_value=id_value)

    @staticmethod
    @db_connector
    def delete(
        conn, 
        table: str, 
        id_field: str, 
        id_value: str):

        sql = f"DELETE FROM {table} WHERE {id_field} = ?"
        cur = conn.execute(sql, (id_value,))
        return cur.rowcount > 0
    
    @staticmethod
    @db_connector
    def create_table_if_not_exists(
        conn, 
        table: str, 
        model: Type[BaseModel], 
        primary_key: Union[str, int],
        unique_fields: Optional[List[str]] = None
    ):

        fields_sql = []
        for name, field in model.model_fields.items():
            raw_type = CRUD._resolve_base_type(field.annotation)
            sql_type = CRUD.type_mapping.get(raw_type, "TEXT")
            line = f"{name} {sql_type}"
            if name == primary_key:
                line += " PRIMARY KEY"
            fields_sql.append(line)

        constraint_clause = ""
        if unique_fields:
            constraint_clause = f",\n  UNIQUE ({', '.join(unique_fields)})"

        create_sql = (
            f"CREATE TABLE IF NOT EXISTS {table} (\n  "
            + ",\n  ".join(fields_sql)
            + constraint_clause
            + "\n);"
        )

        conn.execute(create_sql)
        L.info(f"Table '{table}' created or already exists.")
        return True

    @staticmethod
    @db_connector
    def bulk_insert(
        conn,
        table: str,
        model: Type[BaseModel],
        data_list: List[BaseModel]
        ):
        if not data_list:
            return f"No data to insert into {table}"

        fields = list(data_list[0].model_dump(mode='python').keys())
        placeholders = ', '.join(['?'] * len(fields))
        columns = ', '.join(fields)
        sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"

        successful = 0
        for idx, item in enumerate(data_list):
            try:
                values = tuple(
                    int(v) if isinstance(v, bool)
                    else json.dumps(v) if isinstance(v, list)
                    else v
                    for v in item.model_dump(mode='python').values()
                )
                conn.execute(sql, values)
                successful += 1
            except Exception as e:
                print(f"[ERROR] Row {idx} failed: {e}")
                print(f"Offending values: {item.model_dump(mode='python')}")

        return f"Successfully inserted {successful}/{len(data_list)} records into {table}"
    
    @staticmethod
    @db_connector
    def bulk_update(
        conn,
        table: str,
        id_field: str,
        data_list: List[tuple],
        *,
        param_style: str = "named"  # or 'positional'
    ):
        """
        Flexible bulk update.

        Parameters:
            table (str): The table to update.
            id_field (str): Field name to match on (e.g., 'block_id').
            data_list (List[tuple]): List of (id_value, update_dict) tuples.
            param_style (str): Choose between 'named' or 'positional' parameter style.

        Example:
            data_list = [
                ('abc-123', {'processed': True}),
                ('def-456', {'processed': False, 'tokens': 18}),
            ]
        """
        if not data_list:
            return "No updates to perform."

        total = 0
        for idx, (id_value, updates) in enumerate(data_list):
            try:
                set_clause = ', '.join(f"{k} = ?" for k in updates)
                values = list(updates.values()) + [id_value]
                sql = f"UPDATE {table} SET {set_clause} WHERE {id_field} = ?"
                conn.execute(sql, values)
                total += 1
            except Exception as e:
                print(f"[ERROR] Update {idx} failed for ID {id_value}: {e}")
                print(f"Offending updates: {updates}")

        return f"Successfully updated {total}/{len(data_list)} records in '{table}'"