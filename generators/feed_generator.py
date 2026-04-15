"""Generate Atom RSS feeds from daily reports."""

import json
import logging
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from agents.base import DailyReport

logger = logging.getLogger(__name__)


class FeedGenerator:
    """Generates Atom 1.0 RSS feeds."""

    def __init__(self, config: dict, web_dir: str):
        self.config = config
        self.web_dir = Path(web_dir)
        self.feeds_dir = self.web_dir / "data" / "feeds"
        self.feeds_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = config.get("pipeline", {}).get("base_url", "")

    def generate(self, report: DailyReport):
        """Generate all feed variants."""
        # Main feed with executive summary + top items
        self._generate_main_feed(report)

        # Per-category feeds
        for cat in report.categories:
            self._generate_category_feed(report, cat)

        logger.info(f"Feeds generated in {self.feeds_dir}")

    def _generate_main_feed(self, report: DailyReport):
        """Generate the main summary feed."""
        entries = []

        # Executive summary as first entry
        if report.executive_summary_el or report.executive_summary_en:
            content = ""
            if report.executive_summary_el:
                content += f"<h2>Ελληνικά</h2>{escape(report.executive_summary_el)}"
            if report.executive_summary_en:
                content += f"<h2>English</h2>{escape(report.executive_summary_en)}"

            entries.append(self._make_entry(
                title=f"Ημερήσια Ανασκόπηση - {report.date}",
                content=content,
                url=f"{self.base_url}/?date={report.date}",
                date=report.date,
                entry_id=f"summary-{report.date}",
            ))

        # Top items from each category
        for cat, cat_report in report.categories.items():
            for item in cat_report.top_items[:3]:
                summary_parts = []
                if item.summary_el:
                    summary_parts.append(item.summary_el)
                if item.summary_en:
                    summary_parts.append(item.summary_en)

                entries.append(self._make_entry(
                    title=item.title,
                    content=escape(" | ".join(summary_parts)),
                    url=item.url or f"{self.base_url}/?date={report.date}&item={item.id}",
                    date=str(item.published)[:10] if item.published else report.date,
                    entry_id=item.id,
                    author=item.author,
                ))

        feed_xml = self._build_feed(
            title="Ελληνικά Νέα - Ημερήσια Ανασκόπηση",
            subtitle="Daily Greek News Digest - Bilingual AI Summary",
            feed_url=f"{self.base_url}/data/feeds/main.xml",
            entries=entries,
        )

        with open(self.feeds_dir / "main.xml", "w", encoding="utf-8") as f:
            f.write(feed_xml)

    def _generate_category_feed(self, report: DailyReport, category: str):
        """Generate a feed for a specific category."""
        cat_report = report.categories.get(category)
        if not cat_report:
            return

        entries = []
        for item in cat_report.top_items[:20]:
            summary_parts = []
            if item.summary_el:
                summary_parts.append(item.summary_el)
            if item.summary_en:
                summary_parts.append(item.summary_en)

            entries.append(self._make_entry(
                title=item.title,
                content=escape(" | ".join(summary_parts)),
                url=item.url or f"{self.base_url}/?date={report.date}&item={item.id}",
                date=str(item.published)[:10] if item.published else report.date,
                entry_id=item.id,
                author=item.author,
            ))

        cat_names = {
            "politics": "Πολιτική / Politics",
            "economy": "Οικονομία / Economy",
            "society": "Κοινωνία / Society",
            "world": "Κόσμος / World",
            "culture": "Πολιτισμός / Culture",
            "opinion": "Απόψεις / Opinion",
            "sports": "Αθλητικά / Sports",
            "social": "Social Media",
        }

        feed_xml = self._build_feed(
            title=f"Ελληνικά Νέα - {cat_names.get(category, category.title())}",
            subtitle=f"Greek News - {category.title()} category",
            feed_url=f"{self.base_url}/data/feeds/{category}.xml",
            entries=entries,
        )

        with open(self.feeds_dir / f"{category}.xml", "w", encoding="utf-8") as f:
            f.write(feed_xml)

    def _build_feed(self, title: str, subtitle: str, feed_url: str,
                     entries: list[str]) -> str:
        """Build an Atom 1.0 feed XML."""
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        xml = f'''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{escape(title)}</title>
  <subtitle>{escape(subtitle)}</subtitle>
  <link href="{escape(feed_url)}" rel="self" type="application/atom+xml"/>
  <link href="{escape(self.base_url)}" rel="alternate" type="text/html"/>
  <id>{escape(feed_url)}</id>
  <updated>{now}</updated>
  <generator>Greek News Aggregator</generator>
{"".join(entries)}
</feed>'''
        return xml

    @staticmethod
    def _make_entry(title: str, content: str, url: str, date: str,
                     entry_id: str, author: str = "") -> str:
        """Create a single Atom entry."""
        pub_date = f"{date}T00:00:00Z" if len(date) == 10 else date
        author_xml = f"\n    <author><name>{escape(author)}</name></author>" if author else ""

        return f'''
  <entry>
    <title>{escape(title)}</title>
    <link href="{escape(url)}" rel="alternate" type="text/html"/>
    <id>urn:greek-news:{escape(entry_id)}</id>
    <updated>{pub_date}</updated>{author_xml}
    <content type="html">{content}</content>
  </entry>'''
