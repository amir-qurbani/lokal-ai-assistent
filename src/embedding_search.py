# embedding_search.py
# ----------------------------------------------------------
# En sökmotor som använder AI-embeddings för att hitta
# relevanta dokument baserat på användarens fråga.
# ----------------------------------------------------------

import os
import json
import math
import unicodedata as ud
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
        SELECT f.path, e.vector, e.summary
        FROM embeddings e
        JOIN files f ON e.file_id = f.id
    """)
    rows = cursor.fetchall()
    conn.close()

    results = []
    seen_files = set()

    for name, vector_json, summary in rows:
        normalized_path = os.path.normcase(os.path.normpath(name.strip()))
        if normalized_path in seen_files:
            continue
        seen_files.add(normalized_path)

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

    # ----------------------------------------------------------
    # Slå ihop resultat med samma filnamn (oavsett mapp/accentskillnader)
    # ----------------------------------------------------------
    def norm_title(p):
        return ud.normalize("NFKC", os.path.basename(p)).casefold()

    best_by_title = {}
    for name, summary, sim in results:
        key = norm_title(name)
        if key not in best_by_title or sim > best_by_title[key][2]:
            best_by_title[key] = (name, summary, sim)

    # Ersätt results med de bästa per titel
    results = list(best_by_title.values())
    results.sort(key=lambda x: x[2], reverse=True)

    # ----------------------------------------------------------
    # Skriv ut resultat
    # ----------------------------------------------------------
    print("\n📄 Sökningsresultat (topp 5):\n" + "-" * 60)

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

    # 🧠 Logga sökningen EN gång
    log_search(query, results)


# ----------------------------------------------------------
# Starta programmet
# ----------------------------------------------------------
if __name__ == "__main__":
    embedding_search()
