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
from context_memory import load_search_memory

# Aktiverar färg i terminalen
init(autoreset=True)


# ----------------------------------------------------------
# Hjälpfunktioner för vektorberäkning
# ----------------------------------------------------------

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b) + 1e-9)


# ----------------------------------------------------------
# Huvudfunktion för sökning
# ----------------------------------------------------------

def embedding_search():
    print("🔍 Startar sökning med embeddings...")

    # 🧠 Hämta användarens sökminne
    memory = load_search_memory()
    sorted_item = sorted(memory.items(), key=lambda x: x[1], reverse=True)
    top_words = [w for w, f in sorted_item[:3]]

    print("🧠 Aktivt minne:", memory)

    # 📝 Användarens fråga
    query = input("Ange din sökfråga: ")

    # Skapa embedding för frågan
    query_vector = generate_embedding(query)

    # Hämta embeddings från DB
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

    # ----------------------------------------------------------
    # Loop genom alla dokument
    # ----------------------------------------------------------
    for name, vector_json, summary in rows:

        normalized_path = os.path.normcase(os.path.normpath(name.strip()))
        if normalized_path in seen_files:
            continue
        seen_files.add(normalized_path)

        p = name.lower()

        # Filtrera systemmappar
        if any(s in p for s in ["node_modules", ".asar.unpacked", "license", "github-recovery", ".git"]):
            continue

        if not summary or len(summary) < 60:
            continue

        # 1️⃣ Embedding-vektor
        vector = json.loads(vector_json)

        # 2️⃣ Baspoäng
        base_score = cosine_similarity(query_vector, vector)

        # 3️⃣ Kontextbonus
        context_bonus = 0.0

        # Frekvens-baserad bonus
        for keyword, freq in memory.items():
            if keyword.lower() in name.lower() or keyword.lower() in summary.lower():
                context_bonus += 0.05 * freq

        context_bonus = min(context_bonus, 0.30)

        # Bonus för topp-3 sökord
        for word in top_words:
            if word.lower() in name.lower() or word.lower() in summary.lower():
                context_bonus += 0.05

        # Bonus om frågan finns i texten
        summary_lower = summary.lower()
        count = summary_lower.count(query.lower())
        if count > 0:
            context_bonus += min(0.02 * count, 0.10)

        # 4️⃣ Total score
        total_score = (base_score * 0.8) + (context_bonus * 0.2)

        # 5️⃣ Lägg till som dictionary
        results.append({
            "name": name,
            "summary": summary,
            "base": base_score,
            "bonus": context_bonus,
            "total": total_score
        })

    # ----------------------------------------------------------
    # 🧽 SLÅ IHOP DUBBELFILER (accent-safe + path-safe)
    # ----------------------------------------------------------

    def norm_title(p):
        return ud.normalize("NFKC", os.path.basename(p)).casefold()

    merged = {}
    for item in results:
        key = norm_title(item["name"])

        # Endast fil med högst total score sparas
        if key not in merged or item["total"] > merged[key]["total"]:
            merged[key] = item

    results = list(merged.values())

    # ----------------------------------------------------------
    # Sortera efter total score
    # ----------------------------------------------------------
    results.sort(key=lambda x: x["total"], reverse=True)

    # ----------------------------------------------------------
    # 🖨️ Visa topp-5
    # ----------------------------------------------------------
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

    # 🧠 Logga sökning
    log_search(query, results)


# ----------------------------------------------------------
# Start
# ----------------------------------------------------------
if __name__ == "__main__":
    embedding_search()
