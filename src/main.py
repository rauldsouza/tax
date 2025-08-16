
from pdf_parser import PDFEquityParser
from ui import EquityPLUI
import tkinter as tk

PDF_PATH = "resources/1131593_PNL_20250816-093248_1.pdf"
PDF_PASSWORD = "VER1510"

def main():
    parser = PDFEquityParser(PDF_PATH, PDF_PASSWORD)
    data = parser.extract_equity_details()
    root = tk.Tk()
    root.title("Equity Profit & Loss Details")
    app = EquityPLUI(root, data)
    root.mainloop()

if __name__ == "__main__":
    main()
