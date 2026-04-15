#!/usr/bin/env python3
"""Standalone RSS collector — used by the Cowork scheduled task.
Fetches articles from Kathimerini RSS feeds and saves them as JSON
for the Cowork AI session to analyze."""

import asyncio
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiohttp
import feedparser
from bs4 import BeautifulSoup


DEFAULT_FEEDS = [
    "https://www.kathimerini.gr/feed",
]

CATEGORY_MAP = {
    "politiki": "politics", "politikh": "politics", "πολιτική": "politics",
    "oikonomia": "economy", "oikonomikh": "economy", "οικονομία": "economy",
    "koinonia": "society", "κοινωνία": "society",
    "kosmos": "world", "κόσμος": "world",
    "politismos": "culture", "πολιτισμός": "culture",
    "apopseis": "opinion", "απόψεις": "opinion",
    "athlitika": "sports", "αθλητικά": "sports",
}


async def fetch_feed(session, feed_url, cutoff):
    """Fetch and parse a single RSS feed."""
    items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) GreekNewsAggregator/1.0",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
    try:
        async with session.get(feed_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                print(f"Warning: {feed_url} returned {resp.status}", file=sys.stderr)
                return items
            content = await resp.text()
    except Exception as e:
        print(f"Warning: Failed to fetch {feed_url}: {e}", file=sys.stderr)
        return items

    feed = feedparser.parse(content)

    for entry in feed.entries:
        pub_date = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

        if pub_date and pub_date < cutoff:
            continue

        content_text = ""
        if hasattr(entry, 'content') and entry.content:
            content_text = entry.content[0].get('value', '')
        elif hasattr(entry, 'summary'):
            content_text = entry.summary or ""

        if content_text:
            soup = BeautifulSoup(content_text, 'html.parser')
            content_text = soup.get_text(separator='\n', strip=True)

        # Detect category
        category = ""
        url = entry.get('link', '')
        for key, cat in CATEGORY_MAP.items():
            if key in url.lower():
                category = cat
                break
        if not category and hasattr(entry, 'tags') and entry.tags:
            for tag in entry.tags:
                term = tag.get('term', '').lower()
                for key, cat in CATEGORY_MAP.items():
                    if key in term:
                        category = cat
                        break

        article_id = hashlib.sha256(url.encode()).hexdigest()[:12] if url else ""

        items.append({
            "id": article_id,
            "title": entry.get('title', ''),
            "content": content_text[:1000],
            "url": url,
            "author": entry.get('author', 'Καθημερινή'),
            "published": pub_date.isoformat() if pub_date else None,
            "source": "Kathimerini",
            "source_type": "rss",
            "category_hint": category,
        })

    return items


async def collect(feeds=None, lookback_hours=24):
    """Collect articles from all feeds."""
    feeds = feeds or DEFAULT_FEEDS
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    all_items = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, url, cutoff) for url in feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)

    # Deduplicate
    seen = set()
    unique = []
    for item in all_items:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    return unique


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    lookback = int(sys.argv[2]) if len(sys.argv) > 2 else 24

    # Load custom feeds from config
    feeds = DEFAULT_FEEDS
    config_feeds = Path(__file__).parent.parent / "config" / "rss_feeds.txt"
    if config_feeds.exists():
        custom = [
            line.strip() for line in config_feeds.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        ]
        if custom:
            feeds = custom

    print(f"Collecting articles (lookback: {lookback}h, feeds: {len(feeds)})", file=sys.stderr)
    items = asyncio.run(collect(feeds, lookback))
    print(f"Collected {len(items)} unique articles", file=sys.stderr)

    # Output JSON to stdout
    output = {
        "date": target_date,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "feed_count": len(feeds),
        "article_count": len(items),
        "articles": items,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
