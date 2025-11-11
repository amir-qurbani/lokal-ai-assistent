# ska senare kunna läsa textinnehåll från olika filtyper
import os
import PyPDF2  # för att läsa PDF-filer


def read_file_content(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.pdf':
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ''
                for page in reader.pages:
                    content += (page.extract_text() or '') + '\n'
                return content
        elif ext == '.md':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"❕ Filtypen '{ext}' stöds inte för innehållsläsning."
    except Exception as e:
        return f"❕ Kunde inte läsa filen: {e}"
