from datetime import datetime
import os


def log_search(query, results):
    # Se till att data-mappen finns
    os.makedirs("data", exist_ok=True)

    # Skapa tidsstämpel
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Bestäm loggfil
    log_file = "data/search_log.txt"

    # Öppna filen EN gång och håll den öppen under hela skrivningen
    with open(log_file, "a", encoding="utf-8") as f:
        # Rubrikrad
        f.write(f"\n[{timestamp}] Sökfråga: {query}\n")

        # Topp 3 resultat
        top_results = results[:3]
        for name, summary, score in top_results:
            percent = round(score * 100, 1)  # 👈 multiplicera med 100 här!
            f.write(f" - {name}: {percent}%\n")

        # ✅ Avgränsare måste ligga INNE i with-blocket
        f.write("-" * 60 + "\n")
