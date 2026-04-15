#!/usr/bin/env python3
"""Standalone Kathimerini scraper — used by the Cowork scheduled task.
Scrapes full article text directly from kathimerini.gr section pages.
Targets: ΠΟΛΙΤΙΚΗ, ΟΙΚΟΝΟΜΙΑ, ΚΟΙΝΩΝΙΑ, ΚΟΣΜΟΣ, ΑΠΟΨΕΙΣ, ΠΟΛΙΤΙΣΜΟΣ,
         and the ΣΤΗΛΕΣ/Θεωρείο column.
Fully autonomous — no browser or login needed."""

import asyncio
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup


# Section pages to scrape, mapped to their canonical category names
SECTIONS = [
    ("https://www.kathimerini.gr/politics/",         "politics"),
    ("https://www.kathimerini.gr/economy/",          "economy"),
    ("https://www.kathimerini.gr/society/",          "society"),
    ("https://www.kathimerini.gr/world/",            "world"),
    ("https://www.kathimerini.gr/opinion/",          "opinion"),
    ("https://www.kathimerini.gr/culture/",          "culture"),
    ("https://www.kathimerini.gr/columns/theoreio/", "opinion"),  # Θεωρείο column
]

BASE_URL = "https://www.kathimerini.gr"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

# Max articles to fetch full text for per section (avoids hammering the server)
MAX_ARTICLES_PER_SECTION = 15

# Polite delay between article fetches (seconds)
FETCH_DELAY = 0.4


def is_article_url(href: str) -> bool:
    """Return True if the href looks like a kathimerini article URL."""
    if not href:
        return False
    parsed = urlparse(href)
    path = parsed.path.rstrip("/")
    # Article URLs have a numeric ID segment, e.g. /politics/564176410/slug/
    segments = [s for s in path.split("/") if s]
    return any(s.isdigit() and len(s) >= 6 for s in segments)


def parse_article_date(soup: BeautifulSoup) -> datetime | None:
    """Extract publication datetime from an article page."""
    # Try <time> element with datetime attribute
    time_el = soup.find("time", attrs={"datetime": True})
    if time_el:
        raw = time_el["datetime"]
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(raw[:19], fmt[:len(fmt)])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue

    # Try meta property="article:published_time"
    meta = soup.find("meta", attrs={"property": "article:published_time"})
    if meta and meta.get("content"):
        raw = meta["content"]
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            pass

    # Try JSON-LD datePublished
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict) and "datePublished" in data:
                return datetime.fromisoformat(
                    data["datePublished"].replace("Z", "+00:00")
                )
        except (json.JSONDecodeError, ValueError):
            continue

    return None


def extract_article_text(soup: BeautifulSoup) -> str:
    """Extract main article body text from a kathimerini article page."""
    # Try common article body containers
    selectors = [
        {"class": re.compile(r"article[-_]?(body|content|text)", re.I)},
        {"class": re.compile(r"story[-_]?(body|content|text)", re.I)},
        {"itemprop": "articleBody"},
        {"class": re.compile(r"content[-_]?body", re.I)},
    ]
    body = None
    for attrs in selectors:
        body = soup.find(["div", "article", "section"], attrs=attrs)
        if body:
            break

    if not body:
        # Fallback: use <article> tag if present
        body = soup.find("article")

    if not body:
        # Last resort: grab all <p> tags in the main content area
        body = soup.find("main") or soup

    # Extract paragraphs, skip very short ones (nav, captions, etc.)
    paragraphs = []
    for p in body.find_all("p"):
        text = p.get_text(separator=" ", strip=True)
        if len(text) > 40:  # skip captions / stubs
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def extract_article_links(soup: BeautifulSoup, section_url: str) -> list[str]:
    """Extract article URLs from a section listing page."""
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Make absolute
        if href.startswith("/"):
            href = BASE_URL + href
        elif not href.startswith("http"):
            href = urljoin(section_url, href)
        # Must be on kathimerini.gr (not .com.cy)
        parsed = urlparse(href)
        if "kathimerini.gr" not in parsed.netloc:
            continue
        if "kathimerini.com.cy" in parsed.netloc:
            continue
        if is_article_url(href):
            links.add(href.split("?")[0].split("#")[0])  # strip query/fragment
    return list(links)


async def fetch_html(session: aiohttp.ClientSession, url: str) -> str | None:
    """Fetch a URL and return its HTML content, or None on failure."""
    try:
        async with session.get(
            url,
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=30),
            allow_redirects=True,
        ) as resp:
            if resp.status != 200:
                print(f"Warning: {url} returned HTTP {resp.status}", file=sys.stderr)
                return None
            return await resp.text(errors="replace")
    except Exception as e:
        print(f"Warning: Failed to fetch {url}: {e}", file=sys.stderr)
        return None


async def fetch_article(
    session: aiohttp.ClientSession,
    url: str,
    category: str,
    cutoff: datetime,
) -> dict | None:
    """Fetch a single article page and return a structured dict, or None."""
    html = await fetch_html(session, url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Date check
    pub_date = parse_article_date(soup)
    if pub_date and pub_date < cutoff:
        return None  # Too old

    # Title
    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

    if not title:
        return None  # Can't proceed without a title

    # Clean up title — strip "| Kathimerini" suffixes
    title = re.sub(r"\s*[\|–-]\s*Καθημερινή.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s*[\|–-]\s*kathimerini.*$", "", title, flags=re.IGNORECASE)
    title = title.strip()

    # Full article text
    full_text = extract_article_text(soup)

    # Author
    author = ""
    author_meta = soup.find("meta", attrs={"name": "author"})
    if author_meta and author_meta.get("content"):
        author = author_meta["content"].strip()
    if not author:
        # Try JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict):
                    auth = data.get("author", {})
                    if isinstance(auth, dict):
                        author = auth.get("name", "")
                    elif isinstance(auth, list) and auth:
                        author = auth[0].get("name", "")
                if author:
                    break
            except (json.JSONDecodeError, AttributeError):
                continue
    if not author:
        author = "Καθημερινή"

    # Description / snippet for backward compatibility
    snippet = ""
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        snippet = og_desc["content"].strip()
    if not snippet and full_text:
        snippet = full_text[:400] + ("…" if len(full_text) > 400 else "")

    article_id = hashlib.sha256(url.encode()).hexdigest()[:12]

    return {
        "id": article_id,
        "title": title,
        "content": full_text or snippet,
        "snippet": snippet,
        "url": url,
        "author": author,
        "published": pub_date.isoformat() if pub_date else None,
        "source": "Kathimerini",
        "source_type": "scrape",
        "category_hint": category,
    }


async def scrape_section(
    session: aiohttp.ClientSession,
    section_url: str,
    category: str,
    cutoff: datetime,
) -> list[dict]:
    """Scrape one section listing and fetch full text for recent articles."""
    print(f"  Scraping section: {section_url}", file=sys.stderr)
    html = await fetch_html(session, section_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = extract_article_links(soup, section_url)
    print(f"    Found {len(links)} article links", file=sys.stderr)

    # Limit per section to avoid hammering
    links = links[:MAX_ARTICLES_PER_SECTION]

    articles = []
    for i, url in enumerate(links):
        if i > 0:
            await asyncio.sleep(FETCH_DELAY)
        article = await fetch_article(session, url, category, cutoff)
        if article:
            articles.append(article)

    print(
        f"    Retrieved {len(articles)} articles within time window", file=sys.stderr
    )
    return articles


async def collect(lookback_hours: int = 24) -> list[dict]:
    """Collect articles from all configured sections."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    connector = aiohttp.TCPConnector(limit=5, limit_per_host=3)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Fetch sections sequentially to be polite (not all at once)
        all_items: list[dict] = []
        for section_url, category in SECTIONS:
            items = await scrape_section(session, section_url, category, cutoff)
            all_items.extend(items)
            await asyncio.sleep(1.0)  # pause between sections

    # Deduplicate by URL
    seen: set[str] = set()
    unique: list[dict] = []
    for item in all_items:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    # Sort by published date descending (None dates go to the end)
    unique.sort(key=lambda x: x.get("published") or "", reverse=True)
    return unique


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    lookback = int(sys.argv[2]) if len(sys.argv) > 2 else 24

    print(
        f"Scraping kathimerini.gr sections (lookback: {lookback}h)", file=sys.stderr
    )
    items = asyncio.run(collect(lookback_hours=lookback))
    print(f"Collected {len(items)} unique Kathimerini articles", file=sys.stderr)

    output = {
        "date": target_date,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "feed_count": len(SECTIONS),
        "article_count": len(items),
        "articles": items,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
