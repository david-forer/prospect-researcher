# prospect-researcher

A Claude Code agent that researches a sales prospect before anyone talks to them. Give it a
company and a contact. It reads their website, searches for recent news and hiring signals,
scores how well they fit your ideal customer, and hands back either a draft cold email or a
one-page brief to read before a sales call.

It researches and drafts. A person reviews and sends. Nothing leaves your machine on its own.

On a test list of Milwaukee firms, a data vendor tagged a law firm as 11 to 50 staff and
$1M to $5M revenue. The agent's notes on that row:

```
Fit: Low. Independent research puts headcount around 43, and the firm already has a
VP of Administration and an IT Manager, which cuts against the no-operations-leader
profile. Multi-shareholder firm, not founder-led.
```

That row would have gone out as a cold email from a list tool. Here it gets flagged before
anyone spends time on it.

## Two modes

**Outreach.** One row per prospect in a spreadsheet: a summary of what they do and how big
they are, the likely operational pain with the evidence behind it, a fit score of High,
Medium or Low, a subject line, and a 100 to 150 word email that opens with something
specific to them. Rows are sorted by fit, and a blank Status column lets you work through
them as a queue.

**Pre-call brief.** One screen of markdown to read in the five minutes before a call. It
covers who the person is, what is probably hurting and why, recent triggers, five
discovery questions tied to what it found, where your offer fits, what could derail the
call, and an opening line. It also flags claims on the prospect's site that read as
marketing rather than fact, such as paid awards.

## How it works

Each prospect gets its own copy of the agent, so a batch of 10 runs in parallel and takes
about as long as one. Each copy:

1. Reads your context files: who your ideal customer is, what you sell, and how you write.
2. Fetches the prospect's home page plus up to four inner pages, and the sitemap when the
   navigation is thin.
3. Runs four or five web searches for news, hiring, the contact's background and headcount,
   plus reviews in brief mode.
4. Checks any size or revenue data you passed in against what it found, and says when they
   disagree.
5. Scores fit and writes the email or brief, listing every URL it used.

Two small Python scripts handle the parts that should be predictable. `from_vibe.py`
converts a Vibe Prospecting export, keeping the most senior contact per company.
`build_xlsx.py` turns the agent's JSON into the review spreadsheet.

The agent never invents a fact to fill a gap. If it cannot find something, the Gaps or
Notes field says so. LinkedIn blocks most page fetches, so headcount usually comes from
search snippets and is marked as approximate.

## What you need

- [Claude Code](https://claude.com/claude-code)
- Python 3.10 or newer, with `openpyxl` for the spreadsheet
- Optional: a Vibe Prospecting account for building lists

It runs on your Claude Code plan. There is no separate API key and no paid search service.

## Setup

```bash
git clone https://github.com/david-forer/prospect-researcher.git
cd prospect-researcher
pip install -r requirements.txt
```

Copy the three examples in `context/` and fill them in with your own business:

```
context/icp.example.md    ->  context/icp.md
context/offer.example.md  ->  context/offer.md
context/voice.example.md  ->  context/voice.md
```

Then install the agent:

```bash
python scripts/install_agent.py
```

That copies `agents/prospect-researcher.md` into `~/.claude/agents/` with the path to your
context folder filled in, so the agent works from any Claude Code session. Your filled-in
context files are gitignored.

## Usage

Open Claude Code in this folder and ask in plain language.

- One prospect: "Research Example Plumbing Co, exampleplumbing.com, owner Jordan Lee."
- A batch: drop a CSV in `input/` (see `input/example.csv` for the columns) and say
  "run the researcher on input/my-list.csv".
- A call: "Brief my 2pm call with Jordan Lee at Example Plumbing Co."

Required columns are `Company`, `Website` and `Contact Name`. `City` and `State` stop it
from researching a different company with a similar name. `Notes` is where the best angles
come from, so put in how you found them or what they said.

## Layout

```
agents/     the agent definition, installed to ~/.claude/agents
context/    your ideal customer, offer and voice (examples are public, yours stay local)
scripts/    install, Vibe Prospecting import, spreadsheet builder
input/      CSVs to research
output/     spreadsheets, JSON records and briefs
CLAUDE.md   how Claude Code runs a batch
```

## Limits

- Research quality follows what is public. A company with a thin website and no press gets
  a thin result, and a Low score that says why.
- Small details can vary between runs, such as a city or a founding year taken from
  different sources. Every claim lists its source, so check anything you plan to repeat to
  the prospect.
- It drafts email and stops there. Sending and reply tracking stay with you.

## License

MIT
