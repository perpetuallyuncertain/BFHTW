import sqlite3
from functools import wraps
from pathlib import Path

from BFHTW.utils.logs import get_logger

L = get_logger()

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = ROOT_DIR / "data" / "database.db"

def db_connector(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        finally:
            conn.close()
    return wrapper


