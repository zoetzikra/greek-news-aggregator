"""Bilingual news analyzer for Greek news articles."""

import json
import logging
from string import Template

from agents.base import BaseAnalyzer, CollectedItem, AnalyzedItem, CategoryReport

logger = logging.getLogger(__name__)

# Maximum items per LLM batch
BATCH_SIZE = 20


class NewsAnalyzer(BaseAnalyzer):
    """Analyzes Greek news articles and produces bilingual summaries."""

    CATEGORIES = ["politics", "economy", "society", "world", "culture", "opinion", "sports"]

    def __init__(self, config: dict, llm_client):
        super().__init__(config, llm_client)
        self.prompts = config.get("prompts", {}).get("news_analysis", {})

    async def analyze(self, items: list[CollectedItem], target_date: str
                      ) -> tuple[list[AnalyzedItem], dict[str, CategoryReport]]:
        """Analyze all collected news items in batches."""
        if not items:
            self.logger.warning("No items to analyze")
            return [], {}

        self.logger.info(f"Analyzing {len(items)} news items for {target_date}")

        # Process in batches
        analyzed_items = []
        batches = [items[i:i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]

        for batch_idx, batch in enumerate(batches):
            self.logger.info(f"Processing batch {batch_idx + 1}/{len(batches)} ({len(batch)} items)")
            try:
                batch_results = await self._analyze_batch(batch, target_date, batch_idx)
                analyzed_items.extend(batch_results)
            except Exception as e:
                self.logger.error(f"Error analyzing batch {batch_idx + 1}: {e}")
                # Create basic analyzed items as fallback
                for item in batch:
                    analyzed_items.append(AnalyzedItem(
                        id=item.id,
                        title=item.title,
                        url=item.url,
                        author=item.author,
                        published=item.published,
                        source=item.source,
                        source_type=item.source_type,
                        category=item.metadata.get("category_hint", ""),
                        importance=30,
                        summary_el=item.content[:200] if item.content else item.title,
                        summary_en="",
                        original_content=item.content,
                    ))

        # Build category reports
        category_reports = self._build_category_reports(analyzed_items)

        self.logger.info(f"Analysis complete: {len(analyzed_items)} items across {len(category_reports)} categories")
        return analyzed_items, category_reports

    async def _analyze_batch(self, batch: list[CollectedItem], target_date: str,
                              batch_idx: int) -> list[AnalyzedItem]:
        """Analyze a single batch of items using the LLM."""
        # Format articles for the prompt
        articles_text = self._format_articles(batch)

        system_prompt = self.prompts.get("system", "You are a Greek news analyst.")
        user_prompt_template = self.prompts.get("batch_analysis", "Analyze these articles: ${articles}")

        user_prompt = Template(user_prompt_template).safe_substitute(
            item_count=len(batch),
            date=target_date,
            articles=articles_text,
        )

        response = await self.llm_client.analyze(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            caller=f"news_analyzer_batch_{batch_idx}",
            max_tokens=4096,
            response_format="json",
        )

        return self._parse_analysis_response(response, batch)

    def _format_articles(self, items: list[CollectedItem]) -> str:
        """Format articles for LLM input."""
        formatted = []
        for i, item in enumerate(items):
            content = item.content[:500] if item.content else ""
            formatted.append(
                f"[Article {i + 1}] ID: {item.id}\n"
                f"Title: {item.title}\n"
                f"Source: {item.source}\n"
                f"URL: {item.url}\n"
                f"Content: {content}\n"
            )
        return "\n---\n".join(formatted)

    def _parse_analysis_response(self, response: dict | list,
                                  original_items: list[CollectedItem]) -> list[AnalyzedItem]:
        """Parse LLM analysis response into AnalyzedItems."""
        analyzed = []

        # Handle different response formats
        if isinstance(response, list):
            analyses = response
        elif isinstance(response, dict):
            analyses = response.get("articles", response.get("items", response.get("analyses", [])))
            if not analyses and "raw_response" in response:
                self.logger.warning("Could not parse analysis response")
                analyses = []
        else:
            analyses = []

        # Map analyses back to original items
        for i, item in enumerate(original_items):
            analysis = analyses[i] if i < len(analyses) else {}

            analyzed_item = AnalyzedItem(
                id=item.id,
                title=item.title,
                url=item.url,
                author=item.author,
                published=item.published,
                source=item.source,
                source_type=item.source_type,
                category=analysis.get("category", item.metadata.get("category_hint", "")),
                importance=analysis.get("importance", analysis.get("score", 50)),
                summary_el=analysis.get("summary_el", analysis.get("summary_greek", "")),
                summary_en=analysis.get("summary_en", analysis.get("summary_english", "")),
                tags_el=analysis.get("tags_el", analysis.get("tags_greek", [])),
                tags_en=analysis.get("tags_en", analysis.get("tags_english", [])),
                sentiment=analysis.get("sentiment", "neutral"),
                original_content=item.content,
                metadata=item.metadata,
            )
            analyzed.append(analyzed_item)

        return analyzed

    def _build_category_reports(self, items: list[AnalyzedItem]) -> dict[str, CategoryReport]:
        """Group analyzed items into category reports."""
        categories: dict[str, list[AnalyzedItem]] = {}
        for item in items:
            cat = item.category or "uncategorized"
            categories.setdefault(cat, []).append(item)

        reports = {}
        for cat, cat_items in categories.items():
            # Sort by importance
            cat_items.sort(key=lambda x: x.importance, reverse=True)

            # Collect themes
            all_tags_el = set()
            all_tags_en = set()
            for item in cat_items:
                all_tags_el.update(item.tags_el)
                all_tags_en.update(item.tags_en)

            reports[cat] = CategoryReport(
                category=cat,
                item_count=len(cat_items),
                top_items=cat_items[:10],
                themes_el=list(all_tags_el)[:10],
                themes_en=list(all_tags_en)[:10],
            )

        return reports


class SocialAnalyzer(BaseAnalyzer):
    """Analyzes social media posts about Greek topics."""

    def __init__(self, config: dict, llm_client):
        super().__init__(config, llm_client)
        self.prompts = config.get("prompts", {}).get("social_analysis", {})

    async def analyze(self, items: list[CollectedItem], target_date: str
                      ) -> tuple[list[AnalyzedItem], dict[str, CategoryReport]]:
        """Analyze social media items."""
        if not items:
            return [], {}

        self.logger.info(f"Analyzing {len(items)} social items for {target_date}")

        analyzed_items = []
        batches = [items[i:i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]

        for batch_idx, batch in enumerate(batches):
            try:
                batch_results = await self._analyze_social_batch(batch, target_date, batch_idx)
                analyzed_items.extend(batch_results)
            except Exception as e:
                self.logger.error(f"Error analyzing social batch {batch_idx + 1}: {e}")

        # Build report under "social" category
        report = CategoryReport(
            category="social",
            item_count=len(analyzed_items),
            top_items=sorted(analyzed_items, key=lambda x: x.importance, reverse=True)[:10],
        )

        return analyzed_items, {"social": report} if analyzed_items else {}

    async def _analyze_social_batch(self, batch: list[CollectedItem], target_date: str,
                                     batch_idx: int) -> list[AnalyzedItem]:
        """Analyze a batch of social media posts."""
        posts_text = "\n---\n".join(
            f"[Post {i+1}] ID: {item.id}\nAuthor: {item.author}\n"
            f"Content: {item.content[:300]}\nURL: {item.url}"
            for i, item in enumerate(batch)
        )

        system_prompt = self.prompts.get("system", "You analyze Greek social media trends.")
        user_prompt_template = self.prompts.get("batch_analysis", "Analyze: ${posts}")

        user_prompt = Template(user_prompt_template).safe_substitute(
            item_count=len(batch),
            date=target_date,
            posts=posts_text,
        )

        response = await self.llm_client.analyze(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            caller=f"social_analyzer_batch_{batch_idx}",
            max_tokens=2048,
            response_format="json",
        )

        analyzed = []
        analyses = response if isinstance(response, list) else response.get("posts", [])

        for i, item in enumerate(batch):
            analysis = analyses[i] if i < len(analyses) else {}
            analyzed.append(AnalyzedItem(
                id=item.id,
                title=item.title,
                url=item.url,
                author=item.author,
                published=item.published,
                source=item.source,
                source_type=item.source_type,
                category="social",
                importance=analysis.get("relevance", analysis.get("importance", 40)),
                summary_el=analysis.get("summary_el", ""),
                summary_en=analysis.get("summary_en", ""),
                sentiment=analysis.get("sentiment", "neutral"),
                original_content=item.content,
                metadata=item.metadata,
            ))

        return analyzed
