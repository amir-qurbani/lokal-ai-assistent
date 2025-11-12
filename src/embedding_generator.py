
from database_manager import get_connection
from file_reader import read_file_content
from text_cleaner import clean_text
import json
import random


def embedding_generator(data):

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT f.id, f.name, f.path FROM files f LEFT JOIN embeddings e ON f.id = e.file_id WHERE e.id IS NULL")
    rows = cursor.fetchall()
    conn.close()

    for file_id, name, path in rows:
        text = read_file_content(path)
        ren_text = clean_text(text)
        if ren_text == "":
            continue
        vector = [round(random.uniform(-1, 1), 4) for _ in range(128)]
        summary = ren_text[:250]
        if len(ren_text) < 50:
            summary = ren_text
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO embeddings (file_id, vector, summary)
            VALUES (?, ?, ?)
        ''', (file_id, json.dumps(vector), summary))
        conn.commit()
        conn.close()
        print(
            f"✅ Embedding skapad: {name} (textlängd: {len(ren_text)}, vektorlängd: {len(vector)})")


print("✅ Alla embeddings skapade!")
