from search_logger import show_log_from_db
from embedding_search import embedding_search
from embedding_generator import generate_all_embeddings
import os
from file_saver import save_files_to_db
from database_manager import init_db
from file_cleaner import clean_old_files
from file_analyzer import analyze_file
from file_scanner import scan_files
from colorama import Fore, Style
from app_info import APP_NAME, VERSION, BUILD_DATE


def print_banner():
    print(Fore.CYAN + "===============================")
    print("🤖 " + APP_NAME)
    print("📦 Version: " + VERSION)
    print("🗓️ Byggd: " + BUILD_DATE)
    print("===============================" + Style.RESET_ALL)


init_db()
print_banner()

try:
    while True:
        print(f"\n=== Huvudmeny === v{VERSION}")
        print("1. Skanna filer")
        print("2. Generera embeddings")
        print("3. Söka dokument")
        print("4. Visa logg")
        print("5. Avsluta")

        val = input("Välj ett alternativ (1-5): ")

        if val == "1":
            directory = input("Vilken mapp vill du skanna?")
            files = scan_files(directory)
        elif val == "2":
            print("🔄 Genererar embeddings för skannade filer...")
            generate_all_embeddings()

        elif val == "3":
            print("🔎 Söker dokument baserat på din fråga...")
            embedding_search()
            analyzed_files = []

        elif val == "4":
            print("📜 Visar söklogg från databasen...")
            show_log_from_db()
        elif val == "5":
            print(f"\nTack för att du använde {APP_NAME} 👋")
            print("Lycka till med studierna och ditt examensarbete!")
            break
        else:
            print("⚠️ Ogiltigt val, försök igen.")
except KeyboardInterrupt:
    print("\n⛔ Avbrutet av användaren (Ctrl+C).")
    print(f"Tack för att du använde {APP_NAME} 👋")
    print("Lycka till med studierna och ditt examensarbete!")
