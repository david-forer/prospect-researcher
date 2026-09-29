"""Convert a Vibe Prospecting export into the researcher's input CSV.

Keeps one contact per company, preferring founders, owners, CEOs and presidents, and
carries size, revenue, industry and email status into Notes.

Usage: python from_vibe.py vibe_export.csv [output.csv]
"""
import csv
import sys
from pathlib import Path

RANK = ["founder", "owner", "chief executive", "ceo", "president", "managing", "partner", "principal"]
OUT_COLS = ["Company", "Website", "Contact Name", "Job Title", "Email", "City", "State",
            "LinkedIn URL", "Notes"]


def seniority(title):
    t = (title or "").lower()
    for i, word in enumerate(RANK):
        if word in t:
            return i
    return len(RANK)


def clean(v):
    return (v or "").strip().strip("[]")


def main():
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(src.stem + "_researcher.csv")
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))

    best = {}
    for r in rows:
        key = (r.get("business_domain") or r.get("business_website") or r.get("business_name", "")).lower()
        if key not in best or seniority(r.get("prospect_job_title")) < seniority(best[key].get("prospect_job_title")):
            best[key] = r

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLS)
        w.writeheader()
        for r in best.values():
            notes = [
                f"Vibe: {clean(r.get('business_number_of_employees_range'))} staff",
                f"{clean(r.get('business_yearly_revenue_range'))} revenue",
                clean(r.get("business_naics_description")),
                f"email {r.get('contact_professional_email_status') or 'status unknown'}",
            ]
            w.writerow({
                "Company": r.get("business_name", "").strip(),
                "Website": r.get("business_website", "").strip(),
                "Contact Name": r.get("prospect_full_name", "").strip(),
                "Job Title": r.get("prospect_job_title", "").strip(),
                "Email": r.get("contact_professional_email", "").strip(),
                "City": (r.get("business_city_name") or "").title(),
                "State": (r.get("business_region") or "").title(),
                "LinkedIn URL": r.get("prospect_linkedin", "").strip(),
                "Notes": ". ".join(n for n in notes if n) + ".",
            })
    print(f"{len(rows)} rows in, {len(best)} companies out -> {out}")


if __name__ == "__main__":
    main()
