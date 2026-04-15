#!/usr/bin/env python3
"""Standalone RSS collector — used by the Cowork scheduled task.
Fetches Kathimerini articles via Google News RSS (since kathimerini.gr
shut down their own feeds). Fully autonomous — no browser or login needed."""

import asyncio
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiohttp
import feedparser
from bs4 import BeautifulSoup


# Google News RSS queries targeting Kathimerini (Greek edition)
# Multiple queries cover different sections; deduplication handles overlaps.
GOOGLE_NEWS_QUERIES = [
    "https://news.google.com/rss/search?q=kathimerini&hl=el&gl=GR&ceid=GR:el",
    "https://news.google.com/rss/search?q=site:kathimerini.gr&hl=el&gl=GR&ceid=GR:el",
    "https://news.google.com/rss/search?q=καθημερινή+εφημερίδα&hl=el&gl=GR&ceid=GR:el",
]

# Keep these as fallback / supplementary sources
SUPPLEMENTARY_FEEDS = [
    "https://news.google.com/rss/search?q=Ελλάδα+νέα&hl=el&gl=GR&ceid=GR:el",
]

CATEGORY_MAP = {
    # URL-based hints
    "politiki": "politics", "politics": "politics", "πολιτική": "politics",
    "oikonomia": "economy", "economy": "economy", "οικονομία": "economy",
    "koinonia": "society", "society": "society", "κοινωνία": "society",
    "kosmos": "world", "world": "world", "κόσμος": "world", "διεθνή": "world",
    "politismos": "culture", "culture": "culture", "πολιτισμός": "culture",
    "apopseis": "opinion", "opinion": "opinion", "απόψεις": "opinion",
    "athlitika": "sports", "sports": "sports", "αθλητικά": "sports",
    # Keyword hints in titles
    "βουλή": "politics", "κυβέρνηση": "politics", "εκλογές": "politics",
    "υπουργ": "politics", "πρωθυπουργ": "politics", "μητσοτάκ": "politics",
    "τσίπρ": "politics", "ανδρουλάκ": "politics", "σύριζα": "politics",
    "πασοκ": "politics", "νδ ": "politics",
    "χρηματιστήριο": "economy", "τράπεζα": "economy", "αγορά": "economy",
    "επενδύσεις": "economy", "τουρισμός": "economy", "εξαγωγές": "economy",
    "μισθός": "economy", "ανεργία": "economy", "ΑΕΠ": "economy",
    "ενοίκιο": "society", "στέγαση": "society", "υγεία": "society",
    "εκπαίδευση": "society", "μετανάστευση": "society", "ατύχημα": "society",
    "φωτιά": "society", "σεισμός": "society", "έγκλημα": "society",
    "τραμπ": "world", "ουκρανία": "world", "ρωσία": "world", "ιράν": "world",
    "ισραήλ": "world", "γάζα": "world", "νατο": "world", "ευρώπη": "world",
    "κίνα": "world", "αμερική": "world", "παπάς": "world", "ΟΗΕ": "world",
    "θέατρο": "culture", "κινηματογράφ": "culture", "μουσείο": "culture",
    "βιβλίο": "culture", "μουσική": "culture", "έκθεση": "culture",
    "ποδόσφαιρο": "sports", "μπάσκετ": "sports", "ολυμπιακός": "sports",
    "παναθηναϊκός": "sports", "αεκ": "sports", "εθνική": "sports",
}

# Sources to EXCLUDE (Cyprus Kathimerini is a different paper)
EXCLUDED_SOURCE_DOMAINS = ["kathimerini.com.cy"]


def detect_category(title: str, url: str, tags: list) -> str:
    """Detect article category from title keywords, URL, and tags."""
    text = (title + " " + url + " " + " ".join(tags)).lower()
    for key, cat in CATEGORY_MAP.items():
        if key.lower() in text:
            return cat
    return "society"  # default


def is_kathimerini_gr(entry) -> bool:
    """Return True if the article is from kathimerini.gr (not Cyprus edition)."""
    url = entry.get("link", "")
    source_title = entry.get("source", {}).get("title", "").lower()
    for excluded in EXCLUDED_SOURCE_DOMAINS:
        if excluded in url.lower() or excluded in source_title:
            return False
    # Accept if it mentions kathimerini (but not .com.cy)
    return True


async def fetch_google_news_feed(session, url, cutoff):
    """Fetch and parse a Google News RSS feed."""
    items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
    }
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                print(f"Warning: {url} returned {resp.status}", file=sys.stderr)
                return items
            content = await resp.text()
    except Exception as e:
        print(f"Warning: Failed to fetch {url}: {e}", file=sys.stderr)
        return items

    feed = feedparser.parse(content)
    for entry in feed.entries:
        if not is_kathimerini_gr(entry):
            continue

        pub_date = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

        if pub_date and pub_date < cutoff:
            continue

        title = entry.get("title", "")
        # Google News sometimes appends " - Source Name" to the title
        title = re.sub(r"\s*-\s*Kathimerini\s*$", "", title, flags=re.IGNORECASE)
        title = re.sub(r"\s*-\s*Καθημερινή\s*$", "", title, flags=re.IGNORECASE)

        # Extract real article URL from Google News redirect link
        article_url = entry.get("link", "")

        # Get any tags
        tags = []
        if hasattr(entry, "tags"):
            tags = [t.get("term", "") for t in entry.tags]

        # Detect category
        category = detect_category(title, article_url, tags)

        # Snippet from summary (strip HTML)
        summary_raw = entry.get("summary", "")
        if summary_raw:
            soup = BeautifulSoup(summary_raw, "html.parser")
            snippet = soup.get_text(separator=" ", strip=True)[:500]
        else:
            snippet = ""

        article_id = hashlib.sha256(article_url.encode()).hexdigest()[:12] if article_url else ""

        items.append({
            "id": article_id,
            "title": title,
            "content": snippet,
            "url": article_url,
            "author": entry.get("author", "Καθημερινή"),
            "published": pub_date.isoformat() if pub_date else None,
            "source": "Kathimerini",
            "source_type": "rss",
            "category_hint": category,
        })

    return items


async def collect(feeds=None, lookback_hours=24):
    """Collect articles from all feeds."""
    all_feeds = feeds or (GOOGLE_NEWS_QUERIES + SUPPLEMENTARY_FEEDS)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    all_items = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_google_news_feed(session, url, cutoff) for url in all_feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)

    # Deduplicate by URL
    seen = set()
    unique = []
    for item in all_items:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    # Sort by published date descending
    unique.sort(key=lambda x: x.get("published") or "", reverse=True)
    return unique


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    lookback = int(sys.argv[2]) if len(sys.argv) > 2 else 24

    print(f"Collecting via Google News RSS (lookback: {lookback}h)", file=sys.stderr)
    items = asyncio.run(collect(lookback_hours=lookback))
    print(f"Collected {len(items)} unique Kathimerini articles", file=sys.stderr)

    output = {
        "date": target_date,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "feed_count": len(GOOGLE_NEWS_QUERIES),
        "article_count": len(items),
        "articles": items,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
