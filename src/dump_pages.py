import fitz

PDF_PATH = "resources/1131593_PNL_20250816-093248_1.pdf"
PASSWORD = "VER1510"
OUTPUT = "src/pages_dump.txt"

def dump_pages(start_page=4, end_page=6):
    doc = fitz.open(PDF_PATH)
    with open(OUTPUT, "w", encoding="utf-8") as out:
        if doc.needs_pass:
            ok = doc.authenticate(PASSWORD)
            out.write(f"Authenticated: {ok}\n")
        for p in range(start_page-1, end_page):
            try:
                page = doc.load_page(p)
                text = page.get_text()
                out.write(f"\n--- PAGE {p+1} TEXT START ---\n")
                out.write(text)
                out.write(f"\n--- PAGE {p+1} TEXT END ---\n")
            except Exception as e:
                out.write(f"Error reading page {p+1}: {e}\n")

if __name__ == '__main__':
    dump_pages(4, 6)
