# embedding_search.py
# ----------------------------------------------------------
# En sökmotor som använder AI-embeddings för att hitta
# relevanta dokument baserat på användarens fråga.
# ----------------------------------------------------------

import os
import json
import math
from database_manager import get_connection
from embedding_generator import generate_embedding
from colorama import Fore, Style, init

from search_logger import log_search

# Aktiverar färg i terminalen
init(autoreset=True)


# ----------------------------------------------------------
# Hjälpfunktioner för vektorberäkning
# ----------------------------------------------------------

def dot(a, b):
    """Beräknar skalärprodukt (dot product) mellan två vektorer"""
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    """Beräknar vektorns längd (magnitud)"""
    return math.sqrt(dot(a, a))


def cosine_similarity(a, b):
    """Beräknar cosinuslikhet mellan två vektorer"""
    return dot(a, b) / (norm(a) * norm(b) + 1e-9)


# ----------------------------------------------------------
# Huvudfunktion för sökning
# ----------------------------------------------------------

def embedding_search():
    print("🔍 Startar sökning med embeddings...")
    query = input("Ange din sökfråga: ")

    # Skapar embedding-vektor för frågan
    query_vector = generate_embedding(query)

    # Hämtar embeddings från databasen
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT f.path, e.vector, e.summary
        FROM embeddings e
        JOIN files f ON e.file_id = f.id
    """)
    rows = cursor.fetchall()
    conn.close()

    results = []

    for name, vector_json, summary in rows:
        p = name.lower()

        # Filtrera bort onödiga eller känsliga filer
        if any(s in p for s in ["node_modules", ".asar.unpacked", "license", "github-recovery", ".git"]):
            continue

        # Hoppa över filer med för kort text
        if not summary or len(summary) < 60:
            continue

        # Ladda embedding-vektorn från databasen
        vector = json.loads(vector_json)

        # Beräkna likhet
        similarity = cosine_similarity(query_vector, vector)

        results.append((name, summary, similarity))

    # Sortera resultaten (högst likhet först)
    results.sort(key=lambda x: x[2], reverse=True)

    # ----------------------------------------------------------
    # Skriv ut resultat
    # ----------------------------------------------------------
    print("\n📄 Sökningsresultat (topp 5):\n" + "-" * 60)

    from search_logger import log_search  # Import en gång

    for i, (name, summary, similarity) in enumerate(results[:5], 1):
        percent = round(similarity * 100, 1)

        # 🎨 Färg baserat på likhet
        if percent >= 70:
            color = Fore.GREEN
        elif percent >= 40:
            color = Fore.YELLOW
        else:
            color = Fore.RED

        # 🧾 Skriv ut varje rad
        file_title = os.path.basename(name)
        print(f"{color}{i}. {file_title}")
        print(f"   🔹 Match: {percent}%")
        print(f"   📘 Sammanfattning: {summary[:200]}...")
        print("-" * 60)

# 🧠 När allt är utskrivet → logga sökningen EN gång
    log_search(query, results)


# ----------------------------------------------------------
# Starta programmet
# ----------------------------------------------------------
if __name__ == "__main__":
    embedding_search()
