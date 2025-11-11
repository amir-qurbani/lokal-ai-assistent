import re


def clean_text(text):
    """
    Städar rå text från PDF/Markdown så den blir lätt att läsa och förstå.
    Regler:
    1. Tar bort extra tomma rader (max 1 i rad)
    2. Byter ut flera mellanslag mot 1
    3. Slår ihop onaturliga radbrytningar (t.ex. ett ord per rad)
    4. Tar bort onödiga mellanslag i början/slutet
    5. För .md: tar bort symboler i början (#, -, *)
    6. Tar bort PDF-symboler (■, •, ●, )
    7. Behåller naturliga stycken med luft
    """
    # 🧹 Dela upp texten i rader
    lines = text.splitlines()
    cleaned_lines = []
    previous_line_empty = False

    for line in lines:
        # Trimma varje rad
        line = line.strip()

        # Hoppa över väldigt korta "skräprader" (t.ex. sidnummer)
        if len(line) <= 2 and not line.endswith('.'):
            continue

        # Ta bort markdown-symboler i början (#, -, *)
        line = re.sub(r'^[#\-\*]+\s*', '', line)

        # Ta bort PDF-symboler
        line = re.sub(r'[■•●]', '', line)

        # Byt ut flera mellanslag mot ett
        line = re.sub(r'\s+', ' ', line)

        # 🧠 Slå ihop korta rader (t.ex. "är", "att bygga")
        if len(line.split()) <= 3:
            if cleaned_lines and not cleaned_lines[-1].endswith(('.', ':')):
                cleaned_lines[-1] += ' ' + line
                continue

        # 🧩 Lägg till tom rad innan ny mening som börjar med stor bokstav
        if cleaned_lines and not cleaned_lines[-1].endswith(('.', ':')) and re.match(r'^[A-ZÅÄÖ]', line):
            cleaned_lines.append('')

        # 🚫 Hoppa över dubbla tomrader
        if line == '':
            if not previous_line_empty:
                cleaned_lines.append('')
                previous_line_empty = True
            continue
        else:
            previous_line_empty = False

        # Behåll luft efter rubriker eller meningar som slutar på punkt/kolon
        cleaned_lines.append(line)
        if line.endswith((':', '.')):
            cleaned_lines.append('')

    # 🪄 Slå ihop raderna men bevara stycken
    cleaned_text = '\n\n'.join([l for l in cleaned_lines if l.strip() != ''])

    # 🧽 Trimma text och fixa överdrivna radbrytningar
    cleaned_text = cleaned_text.strip()
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

    return cleaned_text
