import sqlite3
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar, ParamSpec, cast

from BFHTW.utils.logs import get_logger

L = get_logger()

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "data" / "database.db"

def db_connector(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper



