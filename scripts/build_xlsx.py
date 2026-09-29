"""Compile prospect-researcher JSON records into the review workbook.

Usage: python build_xlsx.py records.json [output.xlsx]
records.json is a JSON array of the objects the prospect-researcher agent returns.
"""
import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

COLS = [
    ("Company", "company", 24), ("Contact Name", "contact", 20), ("Email", "email", 28),
    ("Job Title", "job_title", 18), ("Website", "website", 26), ("Research Summary", "summary", 50),
    ("Fit Score", "fit_score", 10), ("Recommended Angle", "recommended_angle", 40),
    ("Subject Line", "subject", 30), ("Email Body", "email_body", 70), ("Status", None, 12),
    ("Notes", "notes", 40), ("Sources", "sources", 40),
]
FIT = {"High": "C6EFCE", "Medium": "FFEB9C", "Low": "FFC7CE"}


def main():
    src = Path(sys.argv[1])
    out_dir = Path(__file__).resolve().parent.parent / "output"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else out_dir / f"{date.today()}_prospects_researched.xlsx"
    records = json.loads(src.read_text(encoding="utf-8"))

    wb = Workbook()
    ws = wb.active
    ws.title = "Prospects"
    ws.append([c[0] for c in COLS])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    order = {"High": 0, "Medium": 1, "Low": 2}
    records.sort(key=lambda r: order.get(r.get("fit_score", "Low"), 3))
    for r in records:
        row = []
        for _, key, _ in COLS:
            v = "" if key is None else r.get(key, "")
            row.append("\n".join(v) if isinstance(v, list) else v)
        ws.append(row)
    for i, (_, _, w) in enumerate(COLS, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = w
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        fit = row[6].value
        if fit in FIT:
            row[6].fill = PatternFill("solid", fgColor=FIT[fit])
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)

    counts = {k: sum(1 for r in records if r.get("fit_score") == k) for k in FIT}
    print("Research complete.")
    print(f"Prospects processed: {len(records)}")
    print(f"High fit: {counts['High']} | Medium: {counts['Medium']} | Low: {counts['Low']}")
    print(f"Output: {out}")


if __name__ == "__main__":
    main()
