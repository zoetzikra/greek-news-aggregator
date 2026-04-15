# Greek News Aggregator

Automated daily Greek news digest powered by AI. Collects articles from Kathimerini (via RSS and PressReader API), analyzes them with Claude Sonnet, and publishes bilingual summaries (Greek + English) to a static website hosted on GitHub Pages.

Based on [AI News Aggregator](https://github.com/flyryan/ai-news-aggregator) by flyryan.

## Features

- **Daily automated collection** from Kathimerini RSS feeds and PressReader API
- **Optional Twitter/X integration** for Greek trending topics
- **AI-powered analysis** using Claude Sonnet: categorization, importance scoring, bilingual summaries
- **Cross-category topic detection** to identify the day's major themes
- **Bilingual output**: Greek and English summaries for every article and the daily briefing
- **Static website** with dark mode, language toggle, category filters, and search
- **RSS feeds** per category (Atom 1.0)
- **GitHub Actions** for fully automated daily runs
- **GitHub Pages** for free hosting

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/greek-news-aggregator.git
cd greek-news-aggregator
cp config/providers.yaml.example config/providers.yaml
# Edit config/providers.yaml with your API keys
```

### 2. Set up secrets

In your GitHub repository settings, add these secrets:

| Secret | Required | Description |
|--------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key for Claude Sonnet |
| `PRESSREADER_API_KEY` | No | PressReader API key (sign up at developers.pressreader.com) |
| `TWITTERAPI_IO_KEY` | No | TwitterAPI.io key for trending topics |

### 3. Enable GitHub Pages

Go to Settings > Pages > Source: GitHub Actions

### 4. Run the pipeline

The pipeline runs automatically at 7:00 AM Athens time daily, or you can trigger it manually from the Actions tab.

#### Local development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="your-key-here"
python3 run_pipeline.py --config-dir ./config --data-dir ./data --web-dir ./web -v
```

#### Frontend development

```bash
cd frontend
npm install
npm run dev
```

## Architecture

```
Pipeline Flow:
  1. Gather    → Kathimerini RSS + PressReader API + Twitter (optional)
  2. Analyze   → Claude Sonnet: categorize, score, summarize (bilingual)
  3. Topics    → Detect cross-category themes
  4. Summary   → Generate executive briefing (Greek + English)
  5. Publish   → JSON data + Atom RSS feeds + Lunr.js search index
  6. Deploy    → GitHub Pages static site
```

## Project Structure

```
greek-news-aggregator/
├── agents/                  # Python pipeline
│   ├── base.py             # Data classes (CollectedItem, AnalyzedItem, etc.)
│   ├── llm_client.py       # Claude Sonnet API client + cost tracking
│   ├── orchestrator.py     # Main pipeline coordinator
│   ├── gatherers/
│   │   ├── kathimerini_gatherer.py  # RSS + PressReader API
│   │   └── twitter_gatherer.py     # Twitter/X trends (optional)
│   ├── analyzers/
│   │   └── news_analyzer.py        # Bilingual analysis + social analysis
│   └── config/
│       └── loader.py               # YAML config + env var substitution
├── generators/              # Output generators
│   ├── json_generator.py   # JSON for SPA frontend
│   ├── feed_generator.py   # Atom RSS feeds
│   └── search_indexer.py   # Lunr.js search index
├── frontend/                # Svelte SPA
│   └── src/routes/         # Pages: home, archive, feeds, about
├── config/                  # Configuration
│   ├── providers.yaml.example
│   ├── prompts.yaml        # LLM prompt templates
│   ├── rss_feeds.txt       # RSS feed URLs
│   └── twitter_accounts.txt
├── .github/workflows/      # GitHub Actions
│   ├── daily-pipeline.yml  # Daily collection + build + deploy
│   └── manual-build.yml    # Manual frontend rebuild
├── web/data/               # Generated data (committed to repo)
├── run_pipeline.py         # CLI entry point
└── requirements.txt
```

## Cost Estimates

With Kathimerini as the sole source (~30-80 articles/day) and Claude Sonnet:

| Component | Estimated Cost |
|-----------|---------------|
| Article analysis | ~$0.10-0.30/day |
| Topic detection | ~$0.02-0.05/day |
| Executive summary | ~$0.02-0.05/day |
| **Total** | **~$0.15-0.40/day** |
| Monthly estimate | ~$5-12/month |

Twitter adds minimal cost (collection is API-based, not LLM-based).

## Customization

### Adding more sources

Edit `config/rss_feeds.txt` to add RSS feed URLs, one per line.

### Changing categories

Edit `CATEGORY_MAP` in `agents/gatherers/kathimerini_gatherer.py`.

### Modifying prompts

Edit `config/prompts.yaml` to customize how the AI analyzes and summarizes articles.

### Adjusting the schedule

Edit the cron expression in `.github/workflows/daily-pipeline.yml`.

## License

MIT
