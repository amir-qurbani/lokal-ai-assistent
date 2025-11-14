# embedding_search.py
# ----------------------------------------------------------

import os
import json
import math
import unicodedata as ud
from database_manager import get_connection
from embedding_generator import generate_embedding
from colorama import Fore, Style, init
from search_logger import log_search

init(autoreset=True)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b) + 1e-9)


def embedding_search():
    print("🔍 Startar sökning med embeddings...")

    # Hämta användarens minne
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT term, frequency
        FROM user_memory
        ORDER BY frequency DESC
        LIMIT 5
    """)
    memory = dict(cursor.fetchall())
    conn.close()

    print("🧠 Aktivt minne:", memory)

    # Embedding för query
    query = input("Ange din sökfråga: ")
    query_vector = generate_embedding(query)

    sorted_item = sorted(memory.items(), key=lambda x: x[1], reverse=True)
    top_words = [w for w, f in sorted_item[:3]]

    # Hämta embeddings för senaste batchen
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.path, e.vector, e.summary
        FROM embeddings e
        JOIN files f ON e.file_id = f.id
        WHERE f.batch_id = (SELECT MAX(batch_id) FROM files)
    """)
    rows = cursor.fetchall()
    conn.close()

    results = []
    seen_files = set()

    # Loop
    for path, vector_json, summary in rows:

        # Hoppa över om ingen embedding finns ännu
        if not vector_json:
            continue

        # Gör summary säker
        summary = summary or ""

        normalized_path = os.path.normcase(os.path.normpath(path.strip()))
        if normalized_path in seen_files:
            continue
        seen_files.add(normalized_path)

        p = path.lower()

        # Filtrera systemmappar
        if any(s in p for s in ["node_modules", ".asar.unpacked", "license", "github-recovery", ".git"]):
            continue

        if len(summary) < 60:
            continue

        # Hämta embedding-vektor
        vector = json.loads(vector_json)

        # Baspoäng
        base_score = cosine_similarity(query_vector, vector)

        # Kontextbonus
        context_bonus = 0.0

        # Frekvensbonus
        for keyword, freq in memory.items():
            if keyword.lower() in path.lower() or keyword.lower() in summary.lower():
                context_bonus += 0.05 * freq

        context_bonus = min(context_bonus, 0.30)

        # Bonus för toppord
        for word in top_words:
            if word.lower() in path.lower() or word.lower() in summary.lower():
                context_bonus += 0.05

        # Bonus om ordet finns i text
        summary_lower = summary.lower()
        count = summary_lower.count(query.lower())
        if count > 0:
            context_bonus += min(0.02 * count, 0.10)

        # Total score
        total_score = (base_score * 0.8) + (context_bonus * 0.2)

        results.append({
            "name": path,
            "summary": summary,
            "base": base_score,
            "bonus": context_bonus,
            "total": total_score
        })

    # Slå ihop dubbletter
    def norm_title(p):
        return ud.normalize("NFKC", os.path.basename(p)).casefold()

    merged = {}
    for item in results:
        key = norm_title(item["name"])
        if key not in merged or item["total"] > merged[key]["total"]:
            merged[key] = item

    results = list(merged.values())

    # Sortera
    results.sort(key=lambda x: x["total"], reverse=True)

    # Visa topp 5
    print("\n📄 Sökningsresultat (topp 5):\n" + "-" * 60)

    for i, item in enumerate(results[:5], 1):
        name = item["name"]
        summary = item["summary"]
        base = item["base"]
        bonus = item["bonus"]
        total = item["total"]

        percent = round(total * 100, 1)

        if percent >= 70:
            color = Fore.GREEN
        elif percent >= 40:
            color = Fore.YELLOW
        else:
            color = Fore.RED

        print(f"{color}{i}. {os.path.basename(name)}")
        print(f"   🔹 Base: {round(base*100, 1)}%")
        print(f"   🔹 Bonus: {round(bonus*100, 1)}%")
        print(f"   🔹 Total: {percent}%")
        print(f"   📘 Sammanfattning: {summary[:200]}...")
        print("-" * 60)

    # Logga sökning
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_memory (term, frequency)
        VALUES (?, 1)
        ON CONFLICT(term)
        DO UPDATE SET frequency = frequency + 1
    """, (query.lower(),))
    conn.commit()
    conn.close()

    log_search(query, results)


if __name__ == "__main__":
    embedding_search()
