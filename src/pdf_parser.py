import fitz  # PyMuPDF
from typing import List, Dict

class PDFEquityParser:
    def __init__(self, pdf_path: str, password: str):
        self.pdf_path = pdf_path
        self.password = password
        self.doc = None

    def open_pdf(self):
        self.doc = fitz.open(self.pdf_path)
        if self.doc.needs_pass:
            success = self.doc.authenticate(self.password)
            print(f"PDF authentication success: {success}")
        else:
            print("PDF does not require password or already unlocked.")

        # Debug: print text from page 4
        try:
            page = self.doc.load_page(3)
            text = page.get_text()
            print("--- Page 4 Text Start ---")
            print(text[:1000])  # Print first 1000 chars for brevity
            print("--- Page 4 Text End ---")
        except Exception as e:
            print(f"Error reading page 4: {e}")

    def extract_equity_details(self, start_page: int = 4, end_page: int = 22) -> List[Dict]:
        import re
        from datetime import datetime
        self.open_pdf()
        results = []
        section_found = False
        isin_re = re.compile(r"\bIN[A-Z0-9]{9,}\b")

        def parse_float(s: str) -> float:
            try:
                return float(s.replace(',', '').strip())
            except:
                return 0.0

        def parse_date(s: str):
            for fmt in ("%d-%b-%y", "%d-%b-%Y", "%d-%m-%y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(s, fmt)
                except:
                    continue
            return None

        for page_num in range(start_page - 1, end_page):
            page = self.doc.load_page(page_num)
            text = page.get_text()
            if not section_found:
                if 'Equity: Profit & Loss Details for FY 2024-25' in text:
                    section_found = True
            if not section_found:
                continue

            lines = [l.strip() for l in text.splitlines() if l.strip()]
            i = 0
            while i < len(lines):
                line = lines[i]
                m = isin_re.search(line)
                security = None
                if not m and i + 1 < len(lines):
                    m = isin_re.search(lines[i + 1])
                    if m:
                        security = line
                        i += 1
                        line = lines[i]
                if m:
                    isin = m.group(0)
                    # extract security if not set
                    if security is None:
                        # take content before ISIN on same line if any
                        sec_part = line.replace(isin, '').strip()
                        if sec_part:
                            security = sec_part
                        else:
                            # fallback: previous non-numeric line
                            k = i - 1
                            security = ''
                            while k >= 0:
                                if not lines[k].isdigit():
                                    security = lines[k]
                                    break
                                k -= 1

                    # Now read the structured fields that follow
                    j = i + 1
                    qty = None
                    sell_date = None
                    sell_rate = None
                    sell_value = None
                    purchase_date = None
                    purchase_rate = None
                    purchase_value = None
                    net_pl = None

                    # qty may appear
                    if j < len(lines) and re.fullmatch(r"\d+", lines[j]):
                        qty = int(lines[j])
                        j += 1

                    # sell date
                    if j < len(lines):
                        sell_date = parse_date(lines[j])
                        j += 1

                    # sale rate/value handling
                    if j < len(lines):
                        # if next line looks like value (two adjacent numbers). Order may vary.
                        if j + 1 < len(lines) and re.search(r"[\d,]+\.\d+", lines[j + 1]):
                            a = parse_float(lines[j])
                            b = parse_float(lines[j + 1])
                            # choose smaller as rate and larger as total value
                            if a <= b:
                                sell_rate = a
                                sell_value = b
                            else:
                                sell_rate = b
                                sell_value = a
                            j += 2
                        else:
                            # only a single numeric present - treat as value
                            num = parse_float(lines[j])
                            sell_value = num
                            j += 1

                    # purchase date
                    if j < len(lines):
                        purchase_date = parse_date(lines[j])
                        j += 1

                    # purchase rate/value
                    if j < len(lines):
                        if j + 1 < len(lines) and re.search(r"[\d,]+\.\d+", lines[j + 1]):
                            a = parse_float(lines[j])
                            b = parse_float(lines[j + 1])
                            if a <= b:
                                purchase_rate = a
                                purchase_value = b
                            else:
                                purchase_rate = b
                                purchase_value = a
                            j += 2
                        else:
                            purchase_value = parse_float(lines[j])
                            j += 1

                    # net profit/loss
                    if j < len(lines) and re.search(r"-?\d+[\d,]*\.\d+", lines[j]):
                        net_pl = parse_float(lines[j])
                        j += 1

                    holding_days = 0
                    if sell_date and purchase_date:
                        holding_days = (sell_date - purchase_date).days

                    profit_loss = net_pl if net_pl is not None else round((sell_value or 0.0) - (purchase_value or 0.0), 2)
                    pl_type = 'Short Term' if holding_days < 365 else 'Long Term'

                    results.append({
                        'security': security,
                        'isin': isin,
                        'qty': qty,
                        'sell_date': sell_date.strftime('%d-%b-%y') if sell_date else '',
                        'sell_rate': sell_rate,
                        'sell_value': sell_value,
                        'purchase_date': purchase_date.strftime('%d-%b-%y') if purchase_date else '',
                        'purchase_rate': purchase_rate,
                        'purchase_value': purchase_value,
                        'holding_period': holding_days,
                        'profit_loss': profit_loss,
                        'type': pl_type,
                    })

                    i = j
                    continue
                i += 1

        return results
