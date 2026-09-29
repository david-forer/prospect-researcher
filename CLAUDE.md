# Prospect Researcher

Researches prospect companies and either drafts a personalized cold email for each or
writes a one-page brief before a sales call. It researches and drafts. A person reviews and
sends. Nothing is ever sent from here.

The research runs through the `prospect-researcher` subagent (`agents/prospect-researcher.md`,
installed to `~/.claude/agents/` by `scripts/install_agent.py`). Its rules for research, fit
scoring and writing live in that file. Business context lives in `context/`.

---

## Inputs

A CSV in `input/` with these columns:

- Required: `Company`, `Website`, `Contact Name`
- Recommended: `Job Title`, `Email`, `City`, `State`, `LinkedIn URL`, `Notes`

If a required column is missing, stop and say which. `Notes` is where the angle usually comes
from: how you found them, who referred them, what they posted.

### Lists from Vibe Prospecting

1. Search in Vibe Prospecting by city, company size, job level (owner, founder, president),
   industry, and contacts with an email. Limit it to one contact per company. Browsing is
   free and exporting costs credits, so check the cost first.
2. Download the full export CSV into `input/`.
3. Run `python scripts/from_vibe.py input/<export>.csv`. It keeps the most senior contact per
   company, maps the columns, and moves size, revenue, industry and email status into Notes.
4. Run the batch on the `_researcher.csv` it writes. Flag `catch_all` emails, which the
   vendor could not fully verify.

Other sources (Apify, a CRM export): map the columns onto the headers above.

---

## Batch run (outreach)

1. Read the CSV and validate the columns.
2. Spawn one `prospect-researcher` per row, in parallel, in batches of up to 10. Pass the
   row's fields as the prompt, one `Field: value` per line.
3. Collect the JSON each one returns into one array. If a return is not valid JSON, retry
   that prospect once, then record it with fit Low and a note.
4. Read every `email_body` before building. These go to real people.
5. Save the array to `output/YYYY-MM-DD_records.json`, then run
   `python scripts/build_xlsx.py output/YYYY-MM-DD_records.json`.
6. Report the counts line the script prints. Move the CSV to `input/done/`.

Single prospect: spawn one `prospect-researcher` and show the result.

## Pre-call briefs

Spawn `prospect-researcher` with `Mode: brief` plus company, website, contact name, call
time, and anything the prospect wrote when booking. For a day of calls, spawn one per call
in parallel. Save each to `output/briefs/YYYY-MM-DD_company-slug.md`.

---

## Output

`output/YYYY-MM-DD_prospects_researched.xlsx`, sorted High to Low. Columns: Company, Contact
Name, Email, Job Title, Website, Research Summary, Fit Score (colored), Recommended Angle,
Subject Line, Email Body, Status (blank, type Approved), Notes, Sources.
