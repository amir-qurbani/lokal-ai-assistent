import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../data/files.db")


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
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            vector TEXT NOT NULL,
            summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
            UNIQUE(file_id)
        )
    ''')

    conn.commit()
    conn.close()


def get_connection():
    return sqlite3.connect(DB_PATH)
