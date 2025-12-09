# embedding_generator.py
# ----------------------
# Denna fil skapar AI-embeddings (vektorer) för alla filer i databasen.
# Varje embedding representerar en text som en lista med 128 tal.
# Dessa används senare för att jämföra texters likhet i embedding_search.py.

from database_manager import get_connection
from file_reader import read_file_content
from text_cleaner import clean_text
import json
import random
from model_loader import get_model


def generate_embedding(text):
    """
    Skapar en riktig AI-embedding för given text med sentence-transformers.
    Texten delas upp i meningar om den är lång.
    """
    model = get_model()

    # Gör texten kortare eller dela upp långa stycken i meningar
    if len(text) > 1000:
        text = text[:1000]

    # Skapa embedding och normalisera automatiskt
    embedding = model.encode([text], normalize_embeddings=True)[
        0]  # [0] = första (enda) vektorn
    return embedding.tolist()


def generate_all_embeddings():
    """
    Hämtar alla filer från databasen som ännu inte har en embedding
    och skapar en embedding + sammanfattning för varje fil.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Hämta filer som saknar embedding
    cursor.execute("""
        SELECT f.id, f.name, f.path
        FROM files f
        LEFT JOIN embeddings e ON f.id = e.file_id
        WHERE e.id IS NULL
    """)
    rows = cursor.fetchall()
    conn.close()

    # Loopa igenom alla filer och skapa embeddings
    for file_id, name, path in rows:
        text = read_file_content(path)
        ren_text = clean_text(text)

        # Hoppa över tomma texter
        if ren_text == "":
            continue

        # Skapa AI-vektor
        vector = generate_embedding(ren_text)

        # Skapa kort sammanfattning
        summary = ren_text[:250] if len(ren_text) >= 50 else ren_text

        # Spara i databasen
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO embeddings (file_id, vector, summary)
            VALUES (?, ?, ?)
        """, (file_id, json.dumps(vector), summary))

        conn.commit()
        conn.close()

        print(f"✅ Embedding skapad: {name} "
              f"(textlängd: {len(ren_text)}, vektorlängd: {len(vector)})")


# Körs endast om filen körs direkt (inte vid import)
if __name__ == "__main__":
    generate_all_embeddings()
    print("✅ Alla embeddings skapade!")
