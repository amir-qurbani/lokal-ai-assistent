from file_cleaner import clean_old_files
from file_analyzer import analyze_file
from file_scanner import scan_files
from database_manager import init_db
from file_saver import save_files_to_db
print("🤖 Välkommen till Amirs Lokala AI-assistent för filhantering!")


# Skannar en mapp
init_db()
# directory_to_scan = r"C:\Users\99amiqur\OneDrive\Desktop\testmapp"
directory_to_scan = r"C:\Users\99amiqur\Downloads"
files_info = scan_files(directory_to_scan)
files_info = analyze_file(files_info)
print(f"🧾 Exempel på age_days: {files_info[0].get('age_days')}")
save_files_to_db(files_info)
clean_old_files(files_info)
print("👋 Tack för att du använde filhanteringsassistenten. Hej då!")
