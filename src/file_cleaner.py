import os
import shutil
from datetime import datetime
from database_manager import get_connection
from logger import log_action


def clean_old_files(threshold_days=30):
    """
    Rensar gamla filer från SENASTE batchen (senaste skanningen).
    - Hämtar filer från databasen
    - Räknar ut age_days själv
    - Flyttar gamla filer till data/.trash
    """

    # 1️⃣ Hämta senaste batch_id
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT IFNULL(MAX(batch_id), 0) FROM files")
    last_batch = cur.fetchone()[0]

    if last_batch == 0:
        print("❌ Inga filer i databasen ännu. Skanna en mapp först.")
        conn.close()
        return []

    # 2️⃣ Hämta alla filer från senaste batchen som inte är markerade som raderade
    cur.execute("""
        SELECT id, path, name, modified_time
        FROM files
        WHERE batch_id = ? AND IFNULL(is_deleted, 0) = 0
    """, (last_batch,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print(f"❌ Hittade inga filer i batch {last_batch}.")
        return []

    now = datetime.now()
    files_info = []

    # 3️⃣ Räkna ut hur gamla filerna är (age_days)
    for file_id, path, name, modified_time in rows:
        try:
            if modified_time:
                mt = datetime.strptime(modified_time, "%Y-%m-%d %H:%M:%S")
            else:
                mt = datetime.fromtimestamp(os.path.getmtime(path))
            age_days = (now - mt).days
        except Exception:
            age_days = 0

        files_info.append({
            "id": file_id,
            "path": path,
            "name": name,
            "age_days": age_days
        })

    # 4️⃣ Välj kandidater som är äldre än threshold_days
    candidates = [f for f in files_info if f["age_days"] > threshold_days]

    if not candidates:
        print(
            f"✅ Inga filer äldre än {threshold_days} dagar i senaste skanningen (batch {last_batch}).")
        return []

    print(
        f"🧹 Hittade {len(candidates)} filer äldre än {threshold_days} dagar i batch {last_batch}:")
    for i, f in enumerate(candidates, start=1):
        print(f"   {i}. {f['name']} ({f['age_days']} dagar gammal)")

    # 5️⃣ Fråga användaren om bekräftelse
    print("\nVill du flytta dessa filer till karantänmappen data/.trash? (ja/nej):")
    confirmation = input().strip().lower()
    if confirmation != "ja":
        print("❌ Flytt avbruten av användaren.")
        return []

    # 6️⃣ Skapa karantänmapp om den inte finns
    TRASH_DIR = "data/.trash"
    if not os.path.exists(TRASH_DIR):
        os.makedirs(TRASH_DIR)

    moved = []
    conn = get_connection()
    cur = conn.cursor()

    # 7️⃣ Flytta filer + markera som raderade i databasen
    for index, file in enumerate(candidates, start=1):
        try:
            dest_path = os.path.join(TRASH_DIR, os.path.basename(file["path"]))
            base, ext = os.path.splitext(dest_path)

            counter = 1
            while os.path.exists(dest_path):
                dest_path = f"{base} ({counter}){ext}"
                counter += 1

            shutil.move(file["path"], dest_path)

            # Markera som "raderad" i databasen
            cur.execute("""
                UPDATE files
                SET is_deleted = 1,
                    age_days = ?
                WHERE id = ?
            """, (file["age_days"], file["id"]))

            print(
                f"   {index}. 🗑️ Flyttade: {file['name']} → {os.path.basename(dest_path)}")
            moved.append(file)

        except Exception as e:
            print(f"   {index}. ❌ Kunde inte flytta {file['name']}: {e}")

    conn.commit()
    conn.close()

    # 8️⃣ Logga åtgärden
    log_action("Flyttade gamla filer till .trash", moved)

    print(
        f"\n✅ Flytt klar! {len(moved)} filer flyttade till {TRASH_DIR}.\n")
    return moved
