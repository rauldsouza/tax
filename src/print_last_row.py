from pdf_parser import PDFEquityParser
import json

PDF_PATH = "resources/1131593_PNL_20250816-093248_1.pdf"
PDF_PASSWORD = "VER1510"

parser = PDFEquityParser(PDF_PATH, PDF_PASSWORD)
rows = parser.extract_equity_details(4, 22)
out = {
    'count': len(rows),
    'last': rows[-1] if rows else None
}

with open('src/last_row.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, default=str, indent=2)

print('Wrote src/last_row.json')
