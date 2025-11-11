from database_manager import get_connection
from file_reader import read_file_content
from text_cleaner import clean_text


def show_preview():
    print("This is a content preview.")
    conn = get_connection()
    cursor = conn.cursor()
# ust nu hämtar du bara name, ext, size —men du måste också ha path, annars vet programmet inte vilken fil som ska öppnas.
    cursor.execute("SELECT name, ext, size, path FROM files LIMIT 5")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("   ❕ Filen kunde inte läsas (saknas kanske?)")
        return
    print("📄 Förhandsgranskning av filinnehåll:")
    for i, (name, ext, size, path) in enumerate(rows, 1):
        print(f"{i}. {name} ({ext}), {size} bytes")
        try:
            content = read_file_content(path)
            content = clean_text(content)
            preview = content[:300]
            print("   Förhandsgranskning av innehåll:")
            for line in preview.splitlines():
                print(f"   {line}")
        except Exception as e:
            print(f"   Kunde inte läsa filinnehåll: {e}")
