import os
import PyPDF2
from log_service import log_action   # så att fel loggas


def read_file_content(path):
    ext = os.path.splitext(path)[1].lower()

    # Filen finns inte
    if not os.path.exists(path):
        log_action(f"Fel: Filen finns inte → {path}")
        return ""

    try:
        if ext == '.txt' or ext == '.md':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext == '.pdf':
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ''
                for page in reader.pages:
                    text = page.extract_text() or ''
                    content += text + '\n'
                return content

        else:
            log_action(f"Varning: Filtypen stöds inte → {ext}")
            return ""

    except Exception as e:
        log_action(f"Fel: Kunde inte läsa filen {path}. Orsak: {e}")
        return ""
