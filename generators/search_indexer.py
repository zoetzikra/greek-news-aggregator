"""Build Lunr.js search index for client-side search."""

import json
import logging
from pathlib import Path

from lunr import lunr

from agents.base import DailyReport

logger = logging.getLogger(__name__)


class SearchIndexer:
    """Builds and maintains a Lunr.js search index."""

    MAX_DAYS = 30  # Rolling window of days to index

    def __init__(self, config: dict, web_dir: str):
        self.config = config
        self.web_dir = Path(web_dir)
        self.data_dir = self.web_dir / "data"

    def update_index(self, report: DailyReport):
        """Update the search index with new report data."""
        # Load existing documents
        docs_path = self.data_dir / "search-documents.json"
        if docs_path.exists():
            with open(docs_path) as f:
                all_docs = json.load(f)
        else:
            all_docs = {}

        # Add new items
        for item in report.all_items:
            doc = {
                "id": item.id,
                "title": item.title,
                "summary_el": item.summary_el,
                "summary_en": item.summary_en,
                "category": item.category,
                "source": item.source,
                "date": report.date,
                "url": item.url,
                "importance": item.importance,
                "tags_el": " ".join(item.tags_el),
                "tags_en": " ".join(item.tags_en),
            }
            all_docs[item.id] = doc

        # Prune old documents (keep last MAX_DAYS)
        index_path = self.data_dir / "index.json"
        if index_path.exists():
            with open(index_path) as f:
                index_data = json.load(f)
            valid_dates = set(index_data.get("dates", [])[:self.MAX_DAYS])
            all_docs = {
                k: v for k, v in all_docs.items()
                if v.get("date", "") in valid_dates
            }

        # Save documents
        with open(docs_path, "w", encoding="utf-8") as f:
            json.dump(all_docs, f, ensure_ascii=False)

        # Build Lunr index
        docs_list = list(all_docs.values())
        if not docs_list:
            logger.warning("No documents to index")
            return

        try:
            idx = lunr(
                ref="id",
                fields=[
                    {"field_name": "title", "boost": 3},
                    {"field_name": "summary_el", "boost": 2},
                    {"field_name": "summary_en", "boost": 2},
                    {"field_name": "tags_el", "boost": 1},
                    {"field_name": "tags_en", "boost": 1},
                    {"field_name": "category", "boost": 1},
                ],
                documents=docs_list,
            )

            # Serialize the index
            index_json = idx.serialize()

            search_index_path = self.data_dir / "search-index.json"
            with open(search_index_path, "w", encoding="utf-8") as f:
                json.dump(index_json, f)

            logger.info(f"Search index updated: {len(docs_list)} documents")

        except Exception as e:
            logger.error(f"Failed to build search index: {e}")
