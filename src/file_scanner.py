import os
from datetime import datetime


def scan_files(directory):

    # Kolla att mappen finns
    if not os.path.exists(directory):
        print("❌ Mappen finns inte.")
        return

    print(f"📂 Söker igenom: {directory}\n")

    # Skapa en lista som ska innehålla information om varje fil
    files_info = []

    #  Gå igenom alla undermappar och filer
    for root, dirs, files in os.walk(directory):
        for filename in files:
            #  Filtrera – ta bara med PDF, MD och TXT filer
            if filename.endswith(".pdf") or filename.endswith(".md") or filename.endswith(".txt"):
                full_path = os.path.join(root, filename)

                #  Kontrollera att filen inte är tom (större än 0 byte)
                if os.path.getsize(full_path) > 0:
                    #  Hämta information om filen
                    file_info = {
                        "name": filename,
                        "path": full_path,
                        # storlek i byte
                        "size": os.path.getsize(full_path),
                        "modified_time": datetime.fromtimestamp(
                            os.path.getmtime(full_path)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    }

                    #  Lägg till denna fil i listan
                    files_info.append(file_info)

                    # Skriv ut lite info direkt till skärmen
                    print(
                        f"🔎 {filename} ({file_info['size']} bytes, ändrad {file_info['modified_time']})")

    # Efter loopen – skriv ut summering
    print(
        f"\n✅ Sökning klar! {len(files_info)} filer hittades i {directory}\n")

    # 🔟 Returnera listan med all info (om du vill använda den senare)
    return files_info


# Anropa funktionen för flera mappar
scan_files(r"C:\Users\99amiqur\Downloads")
