#!/usr/bin/env python3
"""Helper: scrape ONE Kathimerini section. Used by the daily pipeline to
break the long scrape into chunks small enough to fit a single bash call."""

import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone

import aiohttp

# Reuse the scraping primitives from collect_rss.py
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from collect_rss import scrape_section, SECTIONS  # noqa: E402


async def main():
    if len(sys.argv) < 3:
        print("Usage: _collect_one_section.py <section_index> <lookback_hours>", file=sys.stderr)
        sys.exit(1)
    idx = int(sys.argv[1])
    lookback = int(sys.argv[2])
    section_url, category = SECTIONS[idx]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback)
    connector = aiohttp.TCPConnector(limit=5, limit_per_host=3)
    async with aiohttp.ClientSession(connector=connector) as session:
        items = await scrape_section(session, section_url, category, cutoff)
    print(json.dumps(items, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
