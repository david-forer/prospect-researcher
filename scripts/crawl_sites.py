"""Pre-crawl each prospect's website into markdown with Crawl4AI.

Reads a researcher CSV, crawls the home page plus up to four of about, services, team,
blog and careers pages, and writes input/crawled/<slug>.md for the prospect-researcher
agent to read instead of fetching pages one by one.

Run from a Python environment with Crawl4AI installed (pip install crawl4ai, then crawl4ai-setup):
  python scripts/crawl_sites.py input/<file>.csv
"""
import asyncio
import csv
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "input" / "crawled"
WANT = ["about", "team", "people", "leadership", "service", "solution", "what-we-do", "blog", "news", "career", "job"]
MAX_SUBPAGES = 4
MAX_CHARS = 7000


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def pick_links(base, result):
    host = urlparse(base).netloc.replace("www.", "")
    found, seen = [], set()
    for link in result.links.get("internal", []):
        href = link.get("href", "").split("#")[0].rstrip("/")
        if not href or href in seen or urlparse(href).netloc.replace("www.", "") != host:
            continue
        path = urlparse(href).path.lower()
        for i, key in enumerate(WANT):
            if key in path and path.count("/") <= 2:
                found.append((i, href))
                seen.add(href)
                break
    found.sort()
    return [h for _, h in found[:MAX_SUBPAGES]]


def text_of(result):
    return str(result.markdown)[:MAX_CHARS]


async def crawl_one(crawler, row, cfg):
    site = row["Website"].strip()
    url = site if site.startswith("http") else "https://" + site
    home = await crawler.arun(url, config=cfg)
    if not home.success:
        return f"# CRAWL FAILED\n\n{url}: {home.error_message}\n"
    parts = [f"# {row['Company']}\n\n## PAGE: {url}\n\n{text_of(home)}"]
    subs = pick_links(url, home)
    if subs:
        for r in await crawler.arun_many(subs, config=cfg):
            if r.success:
                parts.append(f"## PAGE: {r.url}\n\n{text_of(r)}")
    return "\n\n---\n\n".join(parts)


async def main(csv_path):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    cfg = CrawlerRunConfig(cache_mode=CacheMode.ENABLED, page_timeout=30000)
    ok = 0
    async with AsyncWebCrawler() as crawler:
        for row in rows:
            try:
                body = await crawl_one(crawler, row, cfg)
            except Exception as e:
                body = f"# CRAWL FAILED\n\n{row['Website']}: {e}\n"
            (OUT / f"{slug(row['Company'])}.md").write_text(body, encoding="utf-8")
            good = not body.startswith("# CRAWL FAILED")
            ok += good
            print(f"{'ok  ' if good else 'FAIL'} {row['Company']}")
    print(f"{ok}/{len(rows)} crawled into {OUT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    asyncio.run(main(sys.argv[1]))
