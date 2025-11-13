# Den ska fungera som din minnesmodul
import os


def load_search_memory():
    if not os.path.exists("data/search_log.txt"):
        print("Ingen tidigare sökminne hittades.")
        return ""
    with open("data/search_log.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    memory = {}
    for line in lines:
        if "Sökfråga:" in line:
            parts = line.strip().split("Sökfråga:")
            if len(parts) > 1:
                query = parts[1].strip().lower()
                if query in memory:
                    memory[query] += 1
                else:
                    memory[query] = 1
    return memory
