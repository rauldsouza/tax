import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import csv
from datetime import datetime, date


class EquityPLUI:
    """Tkinter UI to display parsed equity profit & loss rows and export CSV.

    This is the reverted version without the Qty column. It shows Buy/Sell Price
    (per-unit rate when available) and Buy/Sell Value (total trade value).
    """

    def __init__(self, master, rows):
        self.master = master
        self.rows = rows or []
        self.create_widgets()

    def create_widgets(self):
        toolbar = tk.Frame(self.master)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        export_btn = tk.Button(toolbar, text="Export CSV", command=self.export_csv)
        export_btn.pack(side=tk.LEFT, padx=4, pady=4)

        cols = (
            'Security', 'ISIN', 'Buy Date', 'Buy Price', 'Buy Value',
            'Sell Date', 'Sell Price', 'Sell Value', 'Sell>=23-Jul-24',
            'Holding Period', 'Type', 'Profit/Loss'
        )

        self.tree = ttk.Treeview(self.master, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor='w')

        vsb = ttk.Scrollbar(self.master, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.populate_grid()

    def format_currency(self, v):
        if v is None or v == '':
            return ''
        try:
            return f"{float(v):,.2f}"
        except Exception:
            return str(v)

    def export_csv(self):
        default_path = Path.home() / 'Downloads' / 'export.csv'
        fname = filedialog.asksaveasfilename(defaultextension='.csv', initialfile=str(default_path))
        if not fname:
            return
        header = [
            'Security', 'ISIN', 'Buy Date', 'Buy Price', 'Buy Value',
            'Sell Date', 'Sell Price', 'Sell Value', 'Sell>=23-Jul-24',
            'Holding Period', 'Type', 'Profit/Loss'
        ]
        try:
            with open(fname, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(header)
                for r in self.rows:
                    buy_price = r.get('purchase_rate') or r.get('purchase_value') or ''
                    buy_value = r.get('purchase_value') or ''
                    sell_price = r.get('sell_rate') or r.get('sell_value') or ''
                    sell_value = r.get('sell_value') or ''
                    sell_date = r.get('sell_date', '')
                    sd = self.parse_date(sell_date)
                    sell_cutoff = 'Yes' if sd and sd >= date(2024, 7, 23) else 'No' if sd else ''
                    row = [
                        r.get('security', ''), r.get('isin', ''), r.get('purchase_date', ''),
                        buy_price, buy_value, sell_date, sell_price, sell_value,
                        sell_cutoff, r.get('holding_period', ''), r.get('type', ''),
                        self.format_currency(r.get('profit_loss', ''))
                    ]
                    w.writerow(row)
            messagebox.showinfo('Export', f'Exported to {fname}')
        except Exception as e:
            messagebox.showerror('Export error', str(e))

    def parse_date(self, s):
        if not s:
            return None
        if isinstance(s, (datetime, date)):
            return s
        for fmt in ('%d-%b-%y', '%d-%b-%Y', '%d/%m/%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
        try:
            parts = s.replace('/', '-').split('-')
            if len(parts) == 3:
                d = int(parts[0]); m = int(parts[1]); y = int(parts[2])
                if y < 100:
                    y += 2000
                return date(y, m, d)
        except Exception:
            return None

    def populate_grid(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in self.rows:
            buy_price = r.get('purchase_rate') or r.get('purchase_value') or ''
            buy_value = r.get('purchase_value') or ''
            sell_price = r.get('sell_rate') or r.get('sell_value') or ''
            sell_value = r.get('sell_value') or ''
            sell_date = r.get('sell_date', '')
            sd = self.parse_date(sell_date)
            sell_cutoff = 'Yes' if sd and sd >= date(2024, 7, 23) else 'No' if sd else ''
            vals = [
                r.get('security', ''), r.get('isin', ''), r.get('purchase_date', ''),
                buy_price, buy_value, sell_date, sell_price, sell_value,
                sell_cutoff, r.get('holding_period', ''), r.get('type', ''),
                self.format_currency(r.get('profit_loss', ''))
            ]
            self.tree.insert('', 'end', values=vals)

    def show_aggregates(self):
        short_total = 0.0
        long_total = 0.0
        for r in self.rows:
            try:
                v = float(r.get('profit_loss') or 0)
            except Exception:
                v = 0.0
            if r.get('type', '').lower().startswith('short'):
                short_total += v
            else:
                long_total += v
        return {'short': short_total, 'long': long_total}
