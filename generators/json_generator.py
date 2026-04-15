"""Generate JSON data files for the SPA frontend."""

import json
import logging
from datetime import datetime
from pathlib import Path

import nh3

from agents.base import DailyReport

logger = logging.getLogger(__name__)


class JSONGenerator:
    """Generates JSON files consumed by the Svelte SPA."""

    def __init__(self, config: dict, web_dir: str):
        self.config = config
        self.web_dir = Path(web_dir)
        self.data_dir = self.web_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, report: DailyReport):
        """Generate all JSON files for a daily report."""
        date_dir = self.data_dir / report.date
        date_dir.mkdir(parents=True, exist_ok=True)

        # Generate summary.json
        self._generate_summary(report, date_dir)

        # Generate category files
        self._generate_categories(report, date_dir)

        # Update index.json (date manifest)
        self._update_index(report.date)

        logger.info(f"JSON files generated in {date_dir}")

    def _generate_summary(self, report: DailyReport, date_dir: Path):
        """Generate the daily summary JSON."""
        # All items per category, sorted by importance
        top_items_by_cat = {}
        for cat, cat_report in report.categories.items():
            top_items_by_cat[cat] = [
                self._item_to_json(item)
                for item in cat_report.top_items
            ]

        summary = {
            "date": report.date,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "executive_summary": {
                "el": self._sanitize(report.executive_summary_el),
                "en": self._sanitize(report.executive_summary_en),
            },
            "top_topics": [
                {
                    "name": {"el": t.name_el, "en": t.name_en},
                    "description": {
                        "el": self._sanitize(t.description_el),
                        "en": self._sanitize(t.description_en),
                    },
                    "related_items": t.related_item_ids,
                    "importance": t.importance,
                }
                for t in report.top_topics
            ],
            "categories": {
                cat: {
                    "item_count": r.item_count,
                    "themes": {"el": r.themes_el, "en": r.themes_en},
                    "top_items": top_items_by_cat.get(cat, []),
                }
                for cat, r in report.categories.items()
            },
            "stats": report.collection_stats,
            "cost": {
                "total_usd": report.cost_report.get("total_cost_usd", 0),
                "api_calls": report.cost_report.get("total_calls", 0),
            },
        }

        filepath = date_dir / "summary.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    def _generate_categories(self, report: DailyReport, date_dir: Path):
        """Generate per-category JSON files."""
        # Group items by category
        items_by_cat: dict[str, list] = {}
        for item in report.all_items:
            cat = item.category or "uncategorized"
            items_by_cat.setdefault(cat, []).append(item)

        for cat, items in items_by_cat.items():
            # Sort by importance
            items.sort(key=lambda x: x.importance, reverse=True)

            cat_data = {
                "category": cat,
                "date": report.date,
                "item_count": len(items),
                "items": [self._item_to_json(item) for item in items],
            }

            filepath = date_dir / f"{cat}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(cat_data, f, ensure_ascii=False, indent=2)

    def _update_index(self, date: str):
        """Update the date manifest index.json."""
        index_path = self.data_dir / "index.json"

        if index_path.exists():
            with open(index_path) as f:
                index = json.load(f)
        else:
            index = {"dates": [], "last_updated": ""}

        if date not in index["dates"]:
            index["dates"].append(date)
            index["dates"].sort(reverse=True)

        index["last_updated"] = datetime.utcnow().isoformat() + "Z"

        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def _item_to_json(self, item) -> dict:
        """Convert an AnalyzedItem to JSON-safe dict."""
        return {
            "id": item.id,
            "title": self._sanitize(item.title),
            "url": item.url,
            "author": item.author,
            "published": str(item.published) if item.published else None,
            "source": item.source,
            "source_type": item.source_type,
            "category": item.category,
            "importance": item.importance,
            "summary": {
                "el": self._sanitize(item.summary_el),
                "en": self._sanitize(item.summary_en),
            },
            "tags": {
                "el": item.tags_el,
                "en": item.tags_en,
            },
            "sentiment": item.sentiment,
        }

    @staticmethod
    def _sanitize(text: str) -> str:
        """Sanitize HTML content for XSS prevention."""
        if not text:
            return ""
        return nh3.clean(text, tags={"a", "strong", "em", "p", "br", "ul", "ol", "li", "h3", "h4"},
                         attributes={"a": {"href", "title"}})
