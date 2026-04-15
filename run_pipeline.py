#!/usr/bin/env python3
"""Main entry point for the Greek News Aggregator pipeline."""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

from agents.config.loader import load_config
from agents.orchestrator import Orchestrator
from generators.json_generator import JSONGenerator
from generators.feed_generator import FeedGenerator
from generators.search_indexer import SearchIndexer


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(description="Greek News Aggregator Pipeline")
    parser.add_argument("-d", "--date", default=None,
                        help="Target date (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--config-dir", default="./config",
                        help="Configuration directory")
    parser.add_argument("--data-dir", default="./data",
                        help="Data output directory")
    parser.add_argument("--web-dir", default="./frontend/static",
                        help="Web output directory (SvelteKit static assets)")
    parser.add_argument("--lookback", type=int, default=24,
                        help="Hours to look back for content (default: 24)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last checkpoint")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose logging")
    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger("pipeline")

    # Determine target date
    target_date = args.date or os.environ.get("TARGET_DATE") or datetime.now().strftime("%Y-%m-%d")
    lookback = args.lookback or int(os.environ.get("LOOKBACK_HOURS", "24"))

    logger.info(f"Greek News Aggregator - Pipeline Run")
    logger.info(f"Target date: {target_date}")
    logger.info(f"Lookback: {lookback} hours")

    # Load config
    config = load_config(args.config_dir)

    # Ensure directories exist
    Path(args.data_dir).mkdir(parents=True, exist_ok=True)
    Path(args.web_dir).mkdir(parents=True, exist_ok=True)

    # Run pipeline
    orchestrator = Orchestrator(config, args.data_dir, args.web_dir)

    try:
        report = asyncio.run(orchestrator.run(target_date, lookback))
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

    # Generate outputs
    logger.info("Generating JSON output...")
    json_gen = JSONGenerator(config, args.web_dir)
    json_gen.generate(report)

    logger.info("Generating RSS feeds...")
    feed_gen = FeedGenerator(config, args.web_dir)
    feed_gen.generate(report)

    logger.info("Updating search index...")
    search_gen = SearchIndexer(config, args.web_dir)
    search_gen.update_index(report)

    # Print cost summary
    cost = report.cost_report
    logger.info(f"\n{'='*50}")
    logger.info(f"Pipeline Complete!")
    logger.info(f"Date: {target_date}")
    logger.info(f"Items collected: {report.collection_stats.get('total', 0)}")
    logger.info(f"Items analyzed: {len(report.all_items)}")
    logger.info(f"Categories: {len(report.categories)}")
    logger.info(f"Topics detected: {len(report.top_topics)}")
    logger.info(f"API calls: {cost.get('total_calls', 0)}")
    logger.info(f"Total cost: ${cost.get('total_cost_usd', 0):.4f}")
    logger.info(f"{'='*50}")


if __name__ == "__main__":
    main()
