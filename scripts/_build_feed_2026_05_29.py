#!/usr/bin/env python3
"""Generate Atom feed for 2026-05-29 from the per-category JSON files."""

import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

DATE = "2026-05-29"
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "frontend" / "static" / "data" / DATE
FEED_FILE = ROOT / "frontend" / "static" / "data" / "feeds" / "main.xml"
FEED_FILE.parent.mkdir(parents=True, exist_ok=True)

CATS = ["politics", "economy", "society", "world", "opinion", "culture"]


def main():
    items = []
    for cat in CATS:
        f = DATA_DIR / f"{cat}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        items.extend(d.get("items", []))
    # Top 20 by importance
    items.sort(key=lambda x: x.get("importance", 0), reverse=True)
    top = items[:20]

    now = datetime.now(timezone.utc).isoformat()
    parts = []
    parts.append('<?xml version="1.0" encoding="utf-8"?>')
    parts.append('<feed xmlns="http://www.w3.org/2005/Atom">')
    parts.append("  <title>Greek News Aggregator — Daily Top Stories</title>")
    parts.append("  <subtitle>Top stories scraped from kathimerini.gr</subtitle>")
    parts.append('  <link href="https://github.com/zoetzikra/greek-news-aggregator" rel="alternate"/>')
    parts.append('  <link href="https://zoetzikra.github.io/greek-news-aggregator/data/feeds/main.xml" rel="self"/>')
    parts.append(f"  <id>urn:greek-news-aggregator:{DATE}</id>")
    parts.append(f"  <updated>{now}</updated>")
    parts.append("  <author><name>Greek News Aggregator</name></author>")

    for it in top:
        title = escape(it["title"])
        url = escape(it["url"])
        aid = it["id"]
        pub = it.get("published") or now
        author = escape(it.get("author") or "Newsroom")
        cat = escape(it.get("category", ""))
        en = it.get("summary", {}).get("en", "")
        el = it.get("summary", {}).get("el", "")
        summary_text = escape(f"{en} / {el}".strip(" /"))
        parts.append("  <entry>")
        parts.append(f"    <title>{title}</title>")
        parts.append(f'    <link href="{url}"/>')
        parts.append(f"    <id>urn:greek-news-aggregator:{aid}</id>")
        parts.append(f"    <updated>{pub}</updated>")
        parts.append(f"    <published>{pub}</published>")
        parts.append(f"    <author><name>{author}</name></author>")
        parts.append(f'    <category term="{cat}"/>')
        parts.append(f'    <summary type="text">{summary_text}</summary>')
        parts.append("  </entry>")
    parts.append("</feed>")

    FEED_FILE.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {FEED_FILE} with {len(top)} entries")


if __name__ == "__main__":
    main()
