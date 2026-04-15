"""Main orchestrator coordinating the full pipeline."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from string import Template

from agents.base import DailyReport, TopTopic
from agents.llm_client import LLMClient, CostTracker
from agents.gatherers.kathimerini_gatherer import KathimeriniGatherer
from agents.gatherers.twitter_gatherer import TwitterGatherer
from agents.analyzers.news_analyzer import NewsAnalyzer, SocialAnalyzer

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates the full news pipeline: gather → analyze → summarize → publish."""

    def __init__(self, config: dict, data_dir: str, web_dir: str):
        self.config = config
        self.data_dir = Path(data_dir)
        self.web_dir = Path(web_dir)
        self.cost_tracker = CostTracker()
        self.llm_client = LLMClient(config, self.cost_tracker)

        # Initialize gatherers
        self.kathimerini_gatherer = KathimeriniGatherer(config)
        self.twitter_gatherer = TwitterGatherer(config)

        # Initialize analyzers
        self.news_analyzer = NewsAnalyzer(config, self.llm_client)
        self.social_analyzer = SocialAnalyzer(config, self.llm_client)

    async def run(self, target_date: str, lookback_hours: int = 24) -> DailyReport:
        """Run the full pipeline for a given date."""
        logger.info(f"=== Starting pipeline for {target_date} ===")
        report = DailyReport(date=target_date)

        # Phase 1: Gather
        logger.info("Phase 1: Gathering content...")
        news_items, social_items = await self._phase_gather(target_date, lookback_hours)
        report.collection_stats = {
            "news_items": len(news_items),
            "social_items": len(social_items),
            "total": len(news_items) + len(social_items),
        }

        if not news_items and not social_items:
            logger.warning("No items collected. Pipeline complete with empty report.")
            return report

        # Save raw data
        self._save_checkpoint("raw", target_date, {
            "news": [self._item_to_dict(i) for i in news_items],
            "social": [self._item_to_dict(i) for i in social_items],
        })

        # Phase 2: Analyze
        logger.info("Phase 2: Analyzing content...")
        analyzed_news, news_reports = await self.news_analyzer.analyze(news_items, target_date)
        analyzed_social, social_reports = await self.social_analyzer.analyze(social_items, target_date)

        all_analyzed = analyzed_news + analyzed_social
        all_reports = {**news_reports, **social_reports}
        report.all_items = all_analyzed
        report.categories = all_reports

        # Save analysis checkpoint
        self._save_checkpoint("analysis", target_date, {
            "items": [self._analyzed_to_dict(i) for i in all_analyzed],
            "categories": {k: self._report_to_dict(v) for k, v in all_reports.items()},
        })

        # Phase 3: Topic detection
        logger.info("Phase 3: Detecting cross-category topics...")
        report.top_topics = await self._phase_topics(all_analyzed, target_date)

        # Phase 4: Executive summary
        logger.info("Phase 4: Generating executive summary...")
        summary_el, summary_en = await self._phase_summary(all_reports, all_analyzed, target_date)
        report.executive_summary_el = summary_el
        report.executive_summary_en = summary_en

        # Cost report
        report.cost_report = self.cost_tracker.get_report()
        logger.info(f"Pipeline complete. Cost: ${report.cost_report['total_cost_usd']:.4f}")

        return report

    async def _phase_gather(self, target_date: str, lookback_hours: int):
        """Phase 1: Parallel gathering from all sources."""
        news_task = self.kathimerini_gatherer.gather(target_date, lookback_hours)
        social_task = self.twitter_gatherer.gather(target_date, lookback_hours)

        results = await asyncio.gather(news_task, social_task, return_exceptions=True)

        news_items = results[0] if not isinstance(results[0], Exception) else []
        social_items = results[1] if not isinstance(results[1], Exception) else []

        if isinstance(results[0], Exception):
            logger.error(f"News gathering failed: {results[0]}")
        if isinstance(results[1], Exception):
            logger.error(f"Social gathering failed: {results[1]}")

        return news_items, social_items

    async def _phase_topics(self, items, target_date: str) -> list[TopTopic]:
        """Phase 3: Detect cross-category topics."""
        if len(items) < 3:
            return []

        prompts = self.config.get("prompts", {}).get("news_analysis", {})
        template = prompts.get("topic_detection", "Identify themes in: ${items}")

        # Summarize items for topic detection
        items_text = "\n".join(
            f"[{i.id}] ({i.category}) {i.title}: {i.summary_el or i.summary_en or ''}"
            for i in sorted(items, key=lambda x: x.importance, reverse=True)[:50]
        )

        user_prompt = Template(template).safe_substitute(
            date=target_date,
            items=items_text,
        )

        try:
            response = await self.llm_client.analyze(
                system_prompt="You are a theme analyst for Greek news. Return valid JSON.",
                user_prompt=user_prompt,
                caller="topic_detection",
                max_tokens=2048,
                response_format="json",
            )

            topics_data = response if isinstance(response, list) else response.get("topics", response.get("themes", []))
            topics = []
            for t in topics_data:
                topics.append(TopTopic(
                    name_el=t.get("name_el", ""),
                    name_en=t.get("name_en", ""),
                    description_el=t.get("description_el", ""),
                    description_en=t.get("description_en", ""),
                    related_item_ids=t.get("related_item_ids", []),
                    importance=t.get("importance", 50),
                ))
            return topics

        except Exception as e:
            logger.error(f"Topic detection failed: {e}")
            return []

    async def _phase_summary(self, category_reports, all_items, target_date: str) -> tuple[str, str]:
        """Phase 4: Generate bilingual executive summary."""
        prompts = self.config.get("prompts", {}).get("news_analysis", {})
        template = prompts.get("executive_summary", "Summarize: ${top_stories}")

        # Build category summaries text
        cat_text = ""
        for cat, report in category_reports.items():
            cat_text += f"\n## {cat.title()} ({report.item_count} articles)\n"
            for item in report.top_items[:5]:
                cat_text += f"- [{item.importance}] {item.title}\n"
                if item.summary_el:
                    cat_text += f"  EL: {item.summary_el}\n"
                if item.summary_en:
                    cat_text += f"  EN: {item.summary_en}\n"

        # Top stories
        top = sorted(all_items, key=lambda x: x.importance, reverse=True)[:10]
        top_text = "\n".join(
            f"[{i.importance}] {i.title} ({i.category})" for i in top
        )

        user_prompt = Template(template).safe_substitute(
            date=target_date,
            category_summaries=cat_text,
            top_stories=top_text,
        )

        try:
            response = await self.llm_client.analyze(
                system_prompt=prompts.get("system", "You are a Greek news analyst."),
                user_prompt=user_prompt,
                caller="executive_summary",
                max_tokens=4096,
                response_format="text",
            )

            # Try to split into Greek and English sections
            if isinstance(response, str):
                parts = response.split("---")
                if len(parts) >= 2:
                    return parts[0].strip(), parts[1].strip()
                # Try splitting by English/Greek headers
                if "**English" in response or "## English" in response:
                    idx = response.find("**English") if "**English" in response else response.find("## English")
                    return response[:idx].strip(), response[idx:].strip()
                return response, ""

            if isinstance(response, dict):
                return response.get("summary_el", response.get("greek", "")), \
                       response.get("summary_en", response.get("english", ""))

            return str(response), ""

        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return "", ""

    def _save_checkpoint(self, phase: str, target_date: str, data: dict):
        """Save checkpoint data to disk."""
        checkpoint_dir = self.data_dir / "checkpoints" / target_date
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        filepath = checkpoint_dir / f"{phase}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"Checkpoint saved: {filepath}")

    @staticmethod
    def _item_to_dict(item) -> dict:
        return {
            "id": item.id, "title": item.title, "content": item.content[:500],
            "url": item.url, "author": item.author,
            "published": str(item.published) if item.published else None,
            "source": item.source, "source_type": item.source_type,
            "tags": item.tags, "metadata": item.metadata,
        }

    @staticmethod
    def _analyzed_to_dict(item) -> dict:
        return {
            "id": item.id, "title": item.title, "url": item.url,
            "author": item.author,
            "published": str(item.published) if item.published else None,
            "source": item.source, "source_type": item.source_type,
            "category": item.category, "importance": item.importance,
            "summary_el": item.summary_el, "summary_en": item.summary_en,
            "tags_el": item.tags_el, "tags_en": item.tags_en,
            "sentiment": item.sentiment,
        }

    @staticmethod
    def _report_to_dict(report) -> dict:
        return {
            "category": report.category,
            "item_count": report.item_count,
            "themes_el": report.themes_el,
            "themes_en": report.themes_en,
        }
