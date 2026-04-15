"""Twitter/X gatherer for Greek trending topics."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import aiohttp

from agents.base import BaseGatherer, CollectedItem

logger = logging.getLogger(__name__)


class TwitterGatherer(BaseGatherer):
    """Gathers trending Greek topics and tweets from configured accounts."""

    TWITTERAPI_BASE = "https://api.twitterapi.io/twitter"

    def __init__(self, config: dict):
        super().__init__(config)
        twitter_config = config.get("sources", {}).get("twitter", {})
        self.api_key = twitter_config.get("api_key", "")
        self.enabled = twitter_config.get("enabled", False) and bool(self.api_key)
        self.accounts = twitter_config.get("accounts", [])

    async def gather(self, target_date: str, lookback_hours: int = 24) -> list[CollectedItem]:
        """Gather tweets from configured accounts and Greek trends."""
        if not self.enabled:
            self.logger.info("Twitter gathering is disabled or no API key configured")
            return []

        items = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

        async with aiohttp.ClientSession() as session:
            # Fetch from configured accounts
            if self.accounts:
                account_items = await self._gather_accounts(session, cutoff)
                items.extend(account_items)

            # Fetch Greek trending topics
            trend_items = await self._gather_trends(session)
            items.extend(trend_items)

        self.logger.info(f"Twitter gathered {len(items)} items total")
        return items

    async def _gather_accounts(self, session: aiohttp.ClientSession,
                                cutoff: datetime) -> list[CollectedItem]:
        """Fetch recent tweets from configured accounts."""
        items = []
        headers = {"X-API-Key": self.api_key}

        for account in self.accounts:
            account = account.strip().lstrip("@")
            if not account:
                continue

            try:
                url = f"{self.TWITTERAPI_BASE}/user/last_tweets"
                params = {"userName": account, "count": 20}

                async with session.get(url, headers=headers, params=params,
                                       timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        self.logger.warning(f"Twitter API error for @{account}: {resp.status}")
                        continue

                    data = await resp.json()

                tweets = data.get("tweets", data.get("data", []))
                for tweet in tweets:
                    # Parse tweet date
                    pub_date = None
                    created_at = tweet.get("created_at", tweet.get("createdAt", ""))
                    if created_at:
                        try:
                            pub_date = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                        except (ValueError, TypeError):
                            try:
                                pub_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                            except (ValueError, TypeError):
                                pass

                    if pub_date and pub_date < cutoff:
                        continue

                    text = tweet.get("text", tweet.get("full_text", ""))
                    tweet_id = tweet.get("id", tweet.get("id_str", ""))

                    item = CollectedItem(
                        title=f"@{account}: {text[:80]}...",
                        content=text,
                        url=f"https://x.com/{account}/status/{tweet_id}" if tweet_id else "",
                        author=f"@{account}",
                        published=pub_date,
                        source="Twitter/X",
                        source_type="twitter",
                        tags=self._extract_hashtags(text),
                        metadata={
                            "tweet_id": tweet_id,
                            "account": account,
                            "retweet_count": tweet.get("retweet_count", 0),
                            "like_count": tweet.get("favorite_count", tweet.get("like_count", 0)),
                        },
                    )
                    items.append(item)

            except Exception as e:
                self.logger.warning(f"Error fetching tweets from @{account}: {e}")

        return items

    async def _gather_trends(self, session: aiohttp.ClientSession) -> list[CollectedItem]:
        """Fetch trending topics for Greece."""
        items = []
        headers = {"X-API-Key": self.api_key}

        try:
            # Greece WOEID: 23424833
            url = f"{self.TWITTERAPI_BASE}/trends"
            params = {"woeid": 23424833}

            async with session.get(url, headers=headers, params=params,
                                   timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status != 200:
                    self.logger.warning(f"Twitter trends API error: {resp.status}")
                    return items

                data = await resp.json()

            trends = data.get("trends", [])
            for trend in trends[:20]:  # Top 20 trends
                name = trend.get("name", "")
                tweet_volume = trend.get("tweet_volume", 0)

                item = CollectedItem(
                    title=f"Trending: {name}",
                    content=f"Trending topic in Greece: {name} ({tweet_volume or 'N/A'} tweets)",
                    url=trend.get("url", f"https://x.com/search?q={name}"),
                    author="Twitter Trends",
                    published=datetime.now(timezone.utc),
                    source="Twitter/X Trends",
                    source_type="twitter",
                    tags=["trending", "greece"],
                    metadata={
                        "trend_name": name,
                        "tweet_volume": tweet_volume,
                    },
                )
                items.append(item)

        except Exception as e:
            self.logger.warning(f"Error fetching Greek trends: {e}")

        return items

    @staticmethod
    def _extract_hashtags(text: str) -> list[str]:
        """Extract hashtags from tweet text."""
        import re
        return re.findall(r'#(\w+)', text)
