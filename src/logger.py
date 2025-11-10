import os
from datetime import datetime


def log_action(action_type, files, log_path="data/log.txt"):
    # Hitta mappen där loggfilen ligger
    log_dir = os.path.dirname(log_path)

    # Om mappen inte finns → skapa den
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # Om mappen inte finns → skapa den

    with open(log_path, "a", encoding="utf-8") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {action_type} - {len(files)} filer\n")
        for file in files:
            log_file.write(
                f"    - {file['name']}\n"
            )
        log_file.write("\n")
    print(f"📝 Logg uppdaterad: {log_path}")
