"""Base classes for gatherers and analyzers."""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CollectedItem:
    """A single collected news item from any source."""
    id: str = ""
    title: str = ""
    content: str = ""
    url: str = ""
    author: str = ""
    published: Optional[datetime] = None
    source: str = ""
    source_type: str = ""  # "rss", "pressreader", "twitter"
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.id and self.url:
            self.id = hashlib.sha256(self.url.encode()).hexdigest()[:12]
        elif not self.id and self.title:
            self.id = hashlib.sha256(self.title.encode()).hexdigest()[:12]


@dataclass
class AnalyzedItem:
    """An analyzed news item with summaries and scores."""
    id: str = ""
    title: str = ""
    url: str = ""
    author: str = ""
    published: Optional[datetime] = None
    source: str = ""
    source_type: str = ""
    category: str = ""
    importance: int = 0
    summary_el: str = ""
    summary_en: str = ""
    tags_el: list[str] = field(default_factory=list)
    tags_en: list[str] = field(default_factory=list)
    sentiment: str = "neutral"
    original_content: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class CategoryReport:
    """Summary report for a single category."""
    category: str = ""
    summary_el: str = ""
    summary_en: str = ""
    item_count: int = 0
    top_items: list[AnalyzedItem] = field(default_factory=list)
    themes_el: list[str] = field(default_factory=list)
    themes_en: list[str] = field(default_factory=list)


@dataclass
class TopTopic:
    """A cross-category topic/theme."""
    name_el: str = ""
    name_en: str = ""
    description_el: str = ""
    description_en: str = ""
    related_item_ids: list[str] = field(default_factory=list)
    importance: int = 0


@dataclass
class DailyReport:
    """The complete daily output."""
    date: str = ""
    executive_summary_el: str = ""
    executive_summary_en: str = ""
    categories: dict[str, CategoryReport] = field(default_factory=dict)
    top_topics: list[TopTopic] = field(default_factory=list)
    all_items: list[AnalyzedItem] = field(default_factory=list)
    collection_stats: dict = field(default_factory=dict)
    cost_report: dict = field(default_factory=dict)


class BaseGatherer:
    """Base class for all content gatherers."""

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    async def gather(self, target_date: str, lookback_hours: int = 24) -> list[CollectedItem]:
        raise NotImplementedError


class BaseAnalyzer:
    """Base class for all content analyzers."""

    def __init__(self, config: dict, llm_client):
        self.config = config
        self.llm_client = llm_client
        self.logger = logging.getLogger(self.__class__.__name__)

    async def analyze(self, items: list[CollectedItem], target_date: str) -> tuple[list[AnalyzedItem], CategoryReport]:
        raise NotImplementedError
