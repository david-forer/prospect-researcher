"""Install the prospect-researcher agent into Claude Code.

Copies agents/prospect-researcher.md to ~/.claude/agents/ with {{CONTEXT_DIR}} replaced by
the absolute path of this repo's context/ folder, so the agent can run from any session.

Usage: python scripts/install_agent.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "agents" / "prospect-researcher.md"
DEST = Path.home() / ".claude" / "agents" / "prospect-researcher.md"
CONTEXT = ROOT / "context"
NEEDED = ["icp.md", "offer.md", "voice.md"]


def main():
    missing = [n for n in NEEDED if not (CONTEXT / n).exists()]
    if missing:
        print("Missing context files: " + ", ".join(missing))
        print("Copy the matching *.example.md files in context/ and fill them in first.")
        raise SystemExit(1)
    text = SRC.read_text(encoding="utf-8").replace("{{CONTEXT_DIR}}", str(CONTEXT))
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(text, encoding="utf-8")
    print(f"Installed {DEST}")
    print("Restart Claude Code or open /agents to pick it up.")


if __name__ == "__main__":
    main()
