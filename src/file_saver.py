import sqlite3
from database_manager import get_connection
from datetime import datetime
import os


def save_files_to_db(files_info):
    print("🧠 Kör save_files_to_db() ...")
    conn = get_connection()

    for file in files_info:
        try:
            conn.execute('''
                INSERT OR REPLACE INTO files 
                (path, name, ext, size, modified_time, scanned_at, age_days) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                file['path'],
                file['name'],
                file['ext'],
                file['size'],
                file['modified_time'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                file.get('age_days', 0)
            ))
        except sqlite3.Error as e:
            print(f"❌ Fel vid sparande av {file['name']} till databasen: {e}")
    conn.commit()
    conn.close()
    print(
        f"💾 {len(files_info)} filer sparades i databasen (ignorerar ev. dubbletter).")
