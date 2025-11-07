import os
import shutil


def clean_old_files(files_info, threshold_days=30):
    # 🗂️ Sätt sökväg till karantänmappen
    TRASH_DIR = "data/.trash"

    # 🔍 Hitta filer som är äldre än threshold_days
    candidates = [f for f in files_info if f.get(
        'age_days', 0) > threshold_days]

    # Om inga filer är för gamla → avsluta
    if not candidates:
        print(f"✅ Inga filer äldre än {threshold_days} dagar.")
        return []

    # ⚠️ Fråga användaren om de vill fortsätta
    print("Vill du fortsätta och flytta dessa filer till karantänmappen? (ja/nej):")
    confirmation = input().strip().lower()
    if confirmation != 'ja':
        print("❌ Flytt avbruten av användaren.")
        return

    # 📁 Skapa .trash EN gång (inte för varje fil)
    if not os.path.exists(TRASH_DIR):
        os.makedirs(TRASH_DIR)

    # 🚚 Flytta filerna till karantänmappen
    for index, file in enumerate(candidates, start=1):
        try:
            # 1️⃣ Skapa grundsökvägen till destinationen
            dest_path = os.path.join(TRASH_DIR, os.path.basename(file["path"]))

            # 2️⃣ Dela upp namnet (t.ex. "rapport", ".pdf")
            base, ext = os.path.splitext(dest_path)

            # 3️⃣ Om fil redan finns → skapa nytt namn med (1), (2) osv
            counter = 1
            while os.path.exists(dest_path):
                dest_path = f"{base} ({counter}){ext}"
                counter += 1

            # 4️⃣ Flytta filen till den slutliga platsen
            shutil.move(file["path"], dest_path)

            # 5️⃣ Visa var filen hamnade
            print(
                f"   {index}. 🗑️ Flyttade: {file['name']} → {os.path.basename(dest_path)}")

        except Exception as e:
            print(f"   {index}. ❌ Kunde inte flytta {file['name']}: {e}")

    # ✅ Sammanfattning
    print(
        f"\n✅ Flytt klar! {len(candidates)} filer flyttade till {TRASH_DIR}.\n")
    return candidates
