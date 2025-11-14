import os
from datetime import datetime


def scan_files(directory, batch_id):

    if not os.path.exists(directory):
        print("❌ Mappen finns inte.")
        return

    print(f"📂 Söker igenom: {directory}\n")

    files_info = []

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".pdf") or filename.endswith(".md") or filename.endswith(".txt"):
                full_path = os.path.join(root, filename)

                if os.path.getsize(full_path) > 0:
                    file_info = {
                        "name": filename,
                        "path": full_path,
                        "size": os.path.getsize(full_path),
                        "ext": os.path.splitext(filename)[1].lower(),
                        "modified_time": datetime.fromtimestamp(
                            os.path.getmtime(full_path)
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "root_path": directory,
                        "batch_id": batch_id
                    }

                    files_info.append(file_info)

                    print(
                        f"🔎 {filename} ({file_info['size']} bytes, ändrad {file_info['modified_time']})")

    print(
        f"\n✅ Sökning klar! {len(files_info)} filer hittades i {directory}\n")

    return files_info
