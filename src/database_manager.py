import sqlite3
import os
from datetime import datetime

DB_PATH = "data/files.db"


def init_db():
    # skapa mapp om den inte finns
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    # öppna databas
    conn = sqlite3.connect(DB_PATH)
    # skapa tabell
    conn.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            ext TEXT NOT NULL,
            size INTEGER,
            modified_time TEXT,
            scanned_at TEXT,
            is_deleted INTEGER DEFAULT 0,
            age_days INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def get_connection():
    return sqlite3.connect(DB_PATH)
