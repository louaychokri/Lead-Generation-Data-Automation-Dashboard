import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any




def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



