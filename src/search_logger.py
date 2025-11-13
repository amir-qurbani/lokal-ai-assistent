# search_logger.py
# ----------------------------------------------------------
# Loggar sökningar till data/search_log.txt
# ----------------------------------------------------------

import os
from datetime import datetime


import sqlite3
import os
from datetime import datetime
from database_manager import get_connection


def log_search(query, results):
    # Hämta tid
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Om inga resultat – logga tomt
    if len(results) == 0:
        top_result = None
        match_score = 0.0
    else:
        top_result = results[0]["name"]
        match_score = float(results[0]["total"])

    # Spara i SQLite
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO search_logs (query, timestamp, top_result, match_score)
        VALUES (?, ?, ?, ?)
    """, (query, timestamp, top_result, match_score))

    conn.commit()
    conn.close()


def show_log_from_db():
    """Visar de senaste sökningarna från databasen med färg och tydlig layout."""
    from colorama import Fore, Style

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT query, timestamp, top_result, match_score
        FROM search_logs
        ORDER BY id DESC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("📭 Ingen logg hittades i databasen ännu.")
        return

    print("\n📜 --- Senaste sökloggar ---")

    for q, t, r, s in rows:
        score = round(s * 100, 1)
        color = (
            Fore.GREEN if score >= 70
            else Fore.YELLOW if score >= 40
            else Fore.RED
        )

        print(f"{Fore.CYAN}🔎 Fråga:{Style.RESET_ALL} {q}")
        print(f"{Fore.MAGENTA}⏱️ Tid:{Style.RESET_ALL} {t}")
        print(f"{Fore.YELLOW}📄 Toppresultat:{Style.RESET_ALL} {r}")
        print(f"{color}📊 Matchning:{Style.RESET_ALL} {score}%")
        print("-" * 40)

    print("📜 --- Slut på logg ---\n")
