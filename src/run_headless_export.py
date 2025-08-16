from pdf_parser import PDFEquityParser
from ui import EquityPLUI
import tkinter as tk
from pathlib import Path
import pathlib

PDF_PATH = "resources/1131593_PNL_20250816-093248_1.pdf"
PDF_PASSWORD = "VER1510"

def main():
    parser = PDFEquityParser(PDF_PATH, PDF_PASSWORD)
    data = parser.extract_equity_details()

    # Force exports into project workspace for verification
    PROJECT_ROOT = Path(r"c:\Users\Raul\Projects\tax")
    pathlib.Path.home = classmethod(lambda cls: PROJECT_ROOT)

    # run export without showing the main window
    root = tk.Tk()
    root.withdraw()
    ui = EquityPLUI(root, data)
    # suppress messagebox
    from tkinter import messagebox
    messagebox.showinfo = lambda *a, **k: None
    messagebox.showerror = lambda *a, **k: None
    ui.export_csv()
    print(f'Exported parsed data to {PROJECT_ROOT / "Downloads" / "export.csv"}')
    root.destroy()

if __name__ == "__main__":
    main()
