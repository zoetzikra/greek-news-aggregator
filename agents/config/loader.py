"""Configuration loader with environment variable substitution."""

import os
import re
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

ENV_VAR_PATTERN = re.compile(r'\$\{(\w+)\}')


def _substitute_env_vars(value):
    """Recursively substitute ${ENV_VAR} patterns in config values."""
    if isinstance(value, str):
        def replacer(match):
            var_name = match.group(1)
            env_val = os.environ.get(var_name, "")
            if not env_val:
                logger.warning(f"Environment variable {var_name} is not set")
            return env_val
        return ENV_VAR_PATTERN.sub(replacer, value)
    elif isinstance(value, dict):
        return {k: _substitute_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_substitute_env_vars(item) for item in value]
    return value


def load_config(config_dir: str) -> dict:
    """Load and merge all configuration files."""
    config_path = Path(config_dir)
    config = {}

    # Load providers.yaml
    providers_file = config_path / "providers.yaml"
    if providers_file.exists():
        with open(providers_file) as f:
            providers = yaml.safe_load(f) or {}
            config.update(_substitute_env_vars(providers))
    else:
        logger.warning(f"No providers.yaml found at {providers_file}")
        # Use defaults from environment
        config["llm"] = {
            "mode": "anthropic",
            "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "model": "claude-sonnet-4-20250514",
            "timeout": 300,
        }
        config["sources"] = {
            "kathimerini_rss": {"enabled": True, "feeds": []},
            "pressreader": {"api_key": os.environ.get("PRESSREADER_API_KEY", "")},
            "twitter": {"enabled": False},
        }
        config["pipeline"] = {
            "base_url": "",
            "lookback_hours": 24,
            "language": {"source": "el", "summaries": ["el", "en"]},
        }

    # Load prompts.yaml
    prompts_file = config_path / "prompts.yaml"
    if prompts_file.exists():
        with open(prompts_file) as f:
            config["prompts"] = yaml.safe_load(f) or {}

    # Load twitter accounts
    twitter_file = config_path / "twitter_accounts.txt"
    if twitter_file.exists():
        accounts = [
            line.strip() for line in twitter_file.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        ]
        config.setdefault("sources", {}).setdefault("twitter", {})["accounts"] = accounts

    # Load custom RSS feeds
    rss_file = config_path / "rss_feeds.txt"
    if rss_file.exists():
        feeds = [
            line.strip() for line in rss_file.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        ]
        config.setdefault("sources", {}).setdefault("kathimerini_rss", {})["feeds"] = feeds

    return config


def load_prompts(config_dir: str) -> dict:
    """Load prompt templates."""
    prompts_file = Path(config_dir) / "prompts.yaml"
    if prompts_file.exists():
        with open(prompts_file) as f:
            return yaml.safe_load(f) or {}
    return {}
