from datetime import datetime
import os


def analyze_file(files_info):
    total_size = 0
    old_files = []

    print("📊 Filanalys:")

    for file in files_info:
        total_size += file['size']

        modified_dt = datetime.strptime(
            file['modified_time'], '%Y-%m-%d %H:%M:%S')
        difference = datetime.now() - modified_dt
        age_days = difference.days

        file['age_days'] = age_days  # 👈 lägg till i dictionaryn

        if age_days > 30:
            old_files.append(file)

    print(f"   Totalt antal filer: {len(files_info)}")
    print(f"   Total storlek: {total_size} bytes")
    print(f"   Analysdatum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Antal filer äldre än 30 dagar: {len(old_files)}")

    if old_files:
        oldest_file = max(old_files, key=lambda f: f['age_days'])
        print(
            f"   🕓 Äldsta filen: {oldest_file['name']} ({oldest_file['age_days']} dagar gammal)")
    else:
        print("   ✅ Inga filer äldre än 30 dagar hittades.")

    return files_info  # 👈 viktig: returnera listan
