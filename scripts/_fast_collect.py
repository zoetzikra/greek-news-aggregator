#!/usr/bin/env python3
"""Fast wrapper around collect_rss.py - parallelizes section fetches to fit in 45s sandbox."""
import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import collect_rss

collect_rss.FETCH_DELAY = 0.0
collect_rss.MAX_ARTICLES_PER_SECTION = 15

import aiohttp
from bs4 import BeautifulSoup


async def scrape_section_parallel(session, section_url, category, cutoff):
    print(f"  Scraping section: {section_url}", file=sys.stderr)
    html = await collect_rss.fetch_html(session, section_url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    links = collect_rss.extract_article_links(soup, section_url)
    print(f"    Found {len(links)} article links", file=sys.stderr)
    links = links[: collect_rss.MAX_ARTICLES_PER_SECTION]
    tasks = [collect_rss.fetch_article(session, url, category, cutoff) for url in links]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    articles = [r for r in results if r and not isinstance(r, Exception)]
    print(f"    Retrieved {len(articles)} articles within time window", file=sys.stderr)
    return articles


async def collect_fast(lookback_hours: int = 24):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    connector = aiohttp.TCPConnector(limit=30, limit_per_host=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        section_tasks = [
            scrape_section_parallel(session, url, cat, cutoff)
            for url, cat in collect_rss.SECTIONS
        ]
        results = await asyncio.gather(*section_tasks, return_exceptions=True)
    all_items = []
    for r in results:
        if isinstance(r, list):
            all_items.extend(r)
    seen = set()
    unique = []
    for item in all_items:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)
    unique.sort(key=lambda x: x.get("published") or "", reverse=True)
    return unique


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    lookback = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    print(f"Scraping kathimerini.gr sections in parallel (lookback: {lookback}h)", file=sys.stderr)
    items = asyncio.run(collect_fast(lookback_hours=lookback))
    print(f"Collected {len(items)} unique Kathimerini articles", file=sys.stderr)
    output = {
        "date": target_date,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "feed_count": len(collect_rss.SECTIONS),
        "article_count": len(items),
        "articles": items,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
