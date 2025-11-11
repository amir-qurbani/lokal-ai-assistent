from database_manager import get_connection


def show_old_files(min_days=30):
    """Visa alla filer i databasen (max 20 rader)."""
    conn = get_connection()
    cursor = conn.cursor()
# age_days måste vara > 30 dagar för att visas
    cursor.execute("""
        SELECT name, ext, size, modified_time, age_days
        FROM files
        WHERE age_days > ?
        ORDER BY scanned_at DESC
    """, (min_days, ))
# Det gör man genom att lägga till en parameter i funktionen, t.ex. min_days.

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❕ Inga filer hittades i databasen.")
        return

    print(f"📄 Visar {len(rows)} filer:")
    for i, (name, ext, size, modified_time, age_days) in enumerate(rows, 1):
        print(
            f"{i}. {name} ({ext}), {size} bytes, ändrad {modified_time}, {age_days or 0} dagar")


def show_files_by_folder(folder_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, ext, size, modified_time, age_days
        FROM files
        WHERE path LIKE ?
    """, (f"%{folder_name}%",))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"❕ Inga filer hittades i mappen '{folder_name}'.")
        return

    print(f"📁 Visar {len(rows)} filer i mappen '{folder_name}':")
    for i, (name, ext, size, modified_time, age_days) in enumerate(rows, 1):
        print(
            f"{i}. {name} ({ext}), {size} bytes, ändrad {modified_time}, {age_days or 0} dagar")
