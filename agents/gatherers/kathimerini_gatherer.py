"""Kathimerini news gatherer using PressReader API + RSS feeds."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

import aiohttp
import feedparser
from bs4 import BeautifulSoup

from agents.base import BaseGatherer, CollectedItem

logger = logging.getLogger(__name__)


class KathimeriniGatherer(BaseGatherer):
    """Gathers news from Kathimerini via PressReader API and RSS feeds."""

    # Default RSS feeds for kathimerini.gr
    DEFAULT_FEEDS = [
        "https://www.kathimerini.gr/feed",
    ]

    # Category mapping for Kathimerini sections
    CATEGORY_MAP = {
        "politiki": "politics",
        "politikh": "politics",
        "πολιτική": "politics",
        "oikonomia": "economy",
        "oikonomikh": "economy",
        "οικονομία": "economy",
        "koinonia": "society",
        "κοινωνία": "society",
        "kosmos": "world",
        "κόσμος": "world",
        "politismos": "culture",
        "πολιτισμός": "culture",
        "apopseis": "opinion",
        "απόψεις": "opinion",
        "athlitika": "sports",
        "αθλητικά": "sports",
    }

    def __init__(self, config: dict):
        super().__init__(config)
        self.sources_config = config.get("sources", {})
        self.rss_config = self.sources_config.get("kathimerini_rss", {})
        self.pressreader_config = self.sources_config.get("pressreader", {})

    async def gather(self, target_date: str, lookback_hours: int = 24) -> list[CollectedItem]:
        """Gather articles from all configured sources."""
        items = []

        # Collect from RSS feeds
        if self.rss_config.get("enabled", True):
            rss_items = await self._gather_rss(target_date, lookback_hours)
            items.extend(rss_items)
            self.logger.info(f"Collected {len(rss_items)} items from RSS feeds")

        # Collect from PressReader API
        if self.pressreader_config.get("api_key"):
            pr_items = await self._gather_pressreader(target_date, lookback_hours)
            items.extend(pr_items)
            self.logger.info(f"Collected {len(pr_items)} items from PressReader API")

        # Deduplicate by URL
        seen_urls = set()
        unique_items = []
        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)

        self.logger.info(f"Total unique items: {len(unique_items)} (deduped from {len(items)})")
        return unique_items

    async def _gather_rss(self, target_date: str, lookback_hours: int) -> list[CollectedItem]:
        """Gather articles from Kathimerini RSS feeds."""
        feeds = self.rss_config.get("feeds", self.DEFAULT_FEEDS)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        items = []

        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_feed(session, feed_url, cutoff) for feed_url in feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    self.logger.warning(f"Feed fetch error: {result}")
                    continue
                items.extend(result)

        return items

    async def _fetch_feed(self, session: aiohttp.ClientSession, feed_url: str,
                          cutoff: datetime) -> list[CollectedItem]:
        """Fetch and parse a single RSS feed."""
        items = []
        try:
            async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    self.logger.warning(f"Feed {feed_url} returned status {resp.status}")
                    return items
                content = await resp.text()
        except Exception as e:
            self.logger.warning(f"Failed to fetch {feed_url}: {e}")
            return items

        feed = feedparser.parse(content)

        for entry in feed.entries:
            # Parse publication date
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

            # Skip items older than cutoff
            if pub_date and pub_date < cutoff:
                continue

            # Extract content
            content = ""
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].get('value', '')
            elif hasattr(entry, 'summary'):
                content = entry.summary or ""

            # Clean HTML from content
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text(separator='\n', strip=True)

            # Detect category from URL or feed tags
            category = self._detect_category(entry)

            item = CollectedItem(
                title=entry.get('title', ''),
                content=content,
                url=entry.get('link', ''),
                author=entry.get('author', 'Καθημερινή'),
                published=pub_date,
                source="Kathimerini",
                source_type="rss",
                tags=[category] if category else [],
                metadata={
                    "feed_url": feed_url,
                    "category_hint": category,
                },
            )
            items.append(item)

        self.logger.info(f"Parsed {len(items)} items from {feed_url}")
        return items

    async def _gather_pressreader(self, target_date: str, lookback_hours: int) -> list[CollectedItem]:
        """Gather articles from PressReader Discovery API."""
        api_key = self.pressreader_config.get("api_key", "")
        base_url = self.pressreader_config.get("base_url", "https://api.prod.pressreader.com")
        cid = self.pressreader_config.get("publication_cid", "")

        if not api_key:
            self.logger.info("No PressReader API key configured, skipping")
            return []

        items = []
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
        }

        # Calculate date range
        target = datetime.strptime(target_date, "%Y-%m-%d")
        date_from = (target - timedelta(hours=lookback_hours)).strftime("%Y-%m-%d")
        date_to = target.strftime("%Y-%m-%d")

        # Search query - filter by publication
        query = {
            "query": "*",
            "filter": {
                "dateFrom": date_from,
                "dateTo": date_to,
            },
            "offset": 0,
            "limit": 100,
        }

        if cid:
            query["filter"]["cid"] = cid

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/discovery/v1/search",
                    json=query,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        self.logger.warning(f"PressReader API error {resp.status}: {error_text}")
                        return items

                    data = await resp.json()

            # Process results
            articles = data.get("articles", data.get("items", []))
            for article in articles:
                pub_date = None
                date_str = article.get("publishedDate", article.get("date", ""))
                if date_str:
                    try:
                        pub_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        pass

                item = CollectedItem(
                    title=article.get("title", ""),
                    content=article.get("text", article.get("snippet", "")),
                    url=article.get("url", article.get("webUrl", "")),
                    author=article.get("author", "Καθημερινή"),
                    published=pub_date,
                    source="Kathimerini (PressReader)",
                    source_type="pressreader",
                    tags=article.get("categories", []),
                    metadata={
                        "pressreader_id": article.get("id", ""),
                        "section": article.get("section", ""),
                        "page": article.get("page", ""),
                    },
                )
                items.append(item)

            self.logger.info(f"PressReader returned {len(items)} articles")

        except Exception as e:
            self.logger.error(f"PressReader API error: {e}")

        return items

    def _detect_category(self, entry) -> str:
        """Detect article category from RSS entry metadata."""
        # Check tags
        if hasattr(entry, 'tags') and entry.tags:
            for tag in entry.tags:
                term = tag.get('term', '').lower()
                for key, cat in self.CATEGORY_MAP.items():
                    if key in term:
                        return cat

        # Check URL path
        url = entry.get('link', '')
        path = urlparse(url).path.lower()
        for key, cat in self.CATEGORY_MAP.items():
            if key in path:
                return cat

        return ""
