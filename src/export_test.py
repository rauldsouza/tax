import tkinter as tk
from ui import EquityPLUI
from pathlib import Path
import pathlib

# Reuse sample_data from test_ui
sample_data = [
    {"security": "ABC Corp", "isin": "IN0000001", "purchase_date": "01-Jan-24", "purchase_value": 100.0, "sell_date": "01-Jul-24", "sell_value": 120.0, "holding_period": 182, "profit_loss": 20.0},
    {"security": "XYZ Ltd", "isin": "IN0000002", "purchase_date": "01-Jan-23", "purchase_value": 200.0, "sell_date": "01-Feb-24", "sell_value": 180.0, "holding_period": 396, "profit_loss": -20.0},
    {"security": "DEF Inc", "isin": "IN0000003", "purchase_date": "01-Jun-24", "purchase_value": 50.0, "sell_date": "01-Sep-24", "sell_value": 80.0, "holding_period": 92, "profit_loss": 30.0},
    {"security": "GHI PLC", "isin": "IN0000004", "purchase_date": "01-Jan-22", "purchase_value": 300.0, "sell_date": "01-Mar-24", "sell_value": 350.0, "holding_period": 790, "profit_loss": 50.0},
]

# Monkeypatch Path.home to point to project root so export writes here for verification
PROJECT_ROOT = Path(r"c:\Users\Raul\Projects\tax")
pathlib.Path.home = classmethod(lambda cls: PROJECT_ROOT)

root = tk.Tk()
root.withdraw()
ui = EquityPLUI(root, sample_data)
ui.export_csv()
print(f'Exported to {PROJECT_ROOT / "export.csv"}')
root.destroy()

# suppress messagebox popups for automated test
from tkinter import messagebox
messagebox.showinfo = lambda *a, **k: None
messagebox.showerror = lambda *a, **k: None
