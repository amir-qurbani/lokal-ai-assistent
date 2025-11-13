# search_logger.py
# ----------------------------------------------------------
# Loggar sökningar till data/search_log.txt
# ----------------------------------------------------------

import os
from datetime import datetime


def log_search(query, results):
    # Se till att data-mappen finns
    os.makedirs("data", exist_ok=True)

    # Tidsstämpel
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Loggfil
    log_file = "data/search_log.txt"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] Sökfråga: {query}\n")

        # Hämta topp 3 resultat
        for item in results[:3]:
            name = item["name"]
            summary = item["summary"]
            score = round(item["total"] * 100, 1)  # total → procent

            f.write(f" - {name}: {score}%\n")
            f.write(f"   Sammanfattning: {summary[:120]}...\n")

        f.write("-" * 60 + "\n")
