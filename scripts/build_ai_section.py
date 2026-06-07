#!/usr/bin/env python3
"""Build a derived "AI" section for a given day.

AI is not a scraped kathimerini.gr section; AI/tech/automation stories are
scattered across the real sections (economy, world, society, ...). This script
scans the day's already-built per-category JSON files, flags articles related to
AI / technology / automation (broad definition), and CROSS-LISTS them into an
`ai.json` file plus an `ai` entry in summary.json. Articles also remain in their
original section.

Behavior:
  * Cross-list (articles stay in their original section too).
  * Broad scope: core AI + robotics/automation + general tech/digital.
  * Hide on empty days: if no matches, no ai.json is written and no `ai` key is
    added to summary.json (so the frontend chip/section simply doesn't appear).

Usage:
    python3 scripts/build_ai_section.py <YYYY-MM-DD> [data_root]

`data_root` defaults to frontend/static/data (relative to repo root / cwd).
Idempotent: safe to re-run.
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

SECTIONS = ["politics", "economy", "society", "world", "opinion", "culture"]

# --- Detection patterns (case-insensitive, Greek + English). Two tiers:
#
# STRONG: unambiguous AI / advanced-tech terms. Matched ANYWHERE, including the
#   article body and summary — a single mention is a reliable signal.
# WEAK: broad/ambiguous tech terms (drone, digital, technology, automation...).
#   These appear incidentally in non-tech stories (a military "drone strike",
#   "online orders"), so they only count when they appear in the TITLE or TAGS
#   — i.e. the headline subject of the piece — not in summary prose or the body.
# ---
_STRONG = [
    r"τεχνητ\w*\s+νοημοσ\w*",
    r"\bνοημοσ[υύ]ν\w*",
    r"μηχανικ\w*\s+μ[αά]θησ\w*",
    r"machine\s+learning",
    r"deep\s+learning",
    r"\bneural\b",
    r"νευρωνικ\w*",
    r"\bllm[s]?\b",
    r"large\s+language\s+model",
    r"γλωσσικ\w*\s+μοντ[εέ]λ\w*",
    r"generative\s+ai",
    r"παραγωγικ\w*\s+νοημοσ\w*",
    r"chatbot\w*",
    r"chatgpt",
    r"openai",
    r"anthropic",
    r"\bclaude\b",
    r"copilot",
    r"\bai\b",
    r"\ba\.i\.\b",
    r"αλγ[οό]ριθμ\w*",
    r"algorithm\w*",
    r"big\s+data",
    r"ρομπ[οό]τ\w*",
    r"robot\w*",
    r"ρομποτικ\w*",
    r"ημιαγωγ\w*",
    r"semiconductor\w*",
    r"μικροτσ[ιί]π\w*",
    r"κβαντικ\w*\s+υπολογ\w*",
    r"\bquantum\s+comput\w*",
    r"\bgpu[s]?\b",
    r"blockchain",
    r"μπλοκ[\s-]?τσ[εέ]ιν",
    r"κρυπτονομ\w*",
    r"\bcrypto\w*",
    r"\bbitcoin\b",
    r"\bethereum\b",
    r"\bcardano\b",
]
_WEAK = [
    r"\bdrone[s]?\b",
    r"μη\s+επανδρωμ\w*",
    r"αυτοματ(?:οποι|ισμ|οπο[ίι])\w*",
    r"automation",
    r"τεχνολογ\w*",
    r"technolog\w*",
    r"ψηφιακ\w*",
    r"ψηφιοπο[ίι]\w*",
    r"\bdigital\b",
    r"λογισμικ\w*",
    r"\bsoftware\b",
    r"\bcloud\b",
    r"υπολογιστικ\w*\s+ν[εέ]φ\w*",
    r"κυβερν[οω](?:ασφ|επ[ιί]θ|[εέ]γκλ)\w*",
    r"cyber\w*",
    r"startup\w*",
    r"νεοφυ\w*\s+επιχειρ\w*",
    r"\bchip[s]?\b",
    r"\bτσιπ\w*",
]
STRONG = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in _STRONG]
WEAK = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in _WEAK]

# Concept buckets -> bilingual theme labels. Used to describe the AI section
# meaningfully (instead of borrowing the source articles' unrelated tags).
# Order = display priority.
CONCEPTS = [
    ("ai", {"el": "Τεχνητή νοημοσύνη", "en": "Artificial intelligence"},
     [r"τεχνητ\w*\s+νοημοσ\w*", r"\bνοημοσ[υύ]ν\w*", r"μηχανικ\w*\s+μ[αά]θησ\w*",
      r"machine\s+learning", r"deep\s+learning", r"\bneural\b", r"νευρωνικ\w*",
      r"\bllm[s]?\b", r"large\s+language\s+model", r"γλωσσικ\w*\s+μοντ[εέ]λ\w*",
      r"generative\s+ai", r"παραγωγικ\w*\s+νοημοσ\w*", r"chatbot\w*", r"chatgpt",
      r"openai", r"anthropic", r"\bclaude\b", r"copilot", r"\bai\b", r"\ba\.i\.\b"]),
    ("robotics", {"el": "Ρομποτική & drones", "en": "Robotics & drones"},
     [r"ρομπ[οό]τ\w*", r"robot\w*", r"ρομποτικ\w*", r"\bdrone[s]?\b", r"μη\s+επανδρωμ\w*"]),
    ("automation", {"el": "Αυτοματοποίηση", "en": "Automation"},
     [r"αυτοματ(?:οποι|ισμ|οπο[ίι])\w*", r"automation", r"αλγ[οό]ριθμ\w*", r"algorithm\w*"]),
    ("crypto", {"el": "Κρυπτονομίσματα & blockchain", "en": "Crypto & blockchain"},
     [r"blockchain", r"μπλοκ[\s-]?τσ[εέ]ιν", r"κρυπτονομ\w*", r"\bcrypto\w*",
      r"\bbitcoin\b", r"\bethereum\b", r"\bcardano\b"]),
    ("hardware", {"el": "Ημιαγωγοί & υπολογιστές", "en": "Chips & computing"},
     [r"ημιαγωγ\w*", r"semiconductor\w*", r"μικροτσ[ιί]π\w*", r"\bchip[s]?\b",
      r"\bτσιπ\w*", r"\bgpu[s]?\b", r"κβαντικ\w*\s+υπολογ\w*", r"\bquantum\s+comput\w*"]),
    ("cyber", {"el": "Κυβερνοασφάλεια", "en": "Cybersecurity"},
     [r"κυβερν[οω](?:ασφ|επ[ιί]θ|[εέ]γκλ)\w*", r"cyber\w*"]),
    ("digital", {"el": "Ψηφιακή τεχνολογία", "en": "Digital technology"},
     [r"τεχνολογ\w*", r"technolog\w*", r"ψηφιακ\w*", r"ψηφιοπο[ίι]\w*", r"\bdigital\b",
      r"λογισμικ\w*", r"\bsoftware\b", r"\bcloud\b", r"υπολογιστικ\w*\s+ν[εέ]φ\w*",
      r"startup\w*", r"νεοφυ\w*\s+επιχειρ\w*", r"big\s+data"]),
]
CONCEPTS = [(k, lbl, [re.compile(p, re.IGNORECASE | re.UNICODE) for p in pats])
            for k, lbl, pats in CONCEPTS]


def concepts_for(item):
    """Which concept buckets this matched item belongs to (for theme labels)."""
    headline = " ".join([
        item.get("title", ""),
        " ".join(item.get("tags", {}).get("el", []) or []),
        " ".join(item.get("tags", {}).get("en", []) or []),
    ])
    full = " ".join([
        headline,
        item.get("summary", {}).get("el", ""),
        item.get("summary", {}).get("en", ""),
        item.get("content", ""),
    ])
    found = []
    for key, label, pats in CONCEPTS:
        # AI/strong concepts can match anywhere; ambiguous ones only in headline.
        hay = full if key in ("ai", "crypto", "hardware") else headline
        if any(p.search(hay) for p in pats):
            found.append((key, label))
    return found


def matched_terms(item):
    # Title + tags: the headline subject of the article.
    headline = " ".join([
        item.get("title", ""),
        " ".join(item.get("tags", {}).get("el", []) or []),
        " ".join(item.get("tags", {}).get("en", []) or []),
    ])
    # Everything, for strong unambiguous signals.
    full = " ".join([
        headline,
        item.get("summary", {}).get("el", ""),
        item.get("summary", {}).get("en", ""),
        item.get("content", ""),
    ])
    hits = []
    for pat in STRONG:
        m = pat.search(full)
        if m:
            hits.append(m.group(0).lower())
    for pat in WEAK:
        m = pat.search(headline)
        if m:
            hits.append(m.group(0).lower())
    return hits


FLAT_KEYS = ("id", "title", "url", "source", "published", "category",
             "importance", "summary", "tags", "sentiment")


def flat(item):
    return {k: item.get(k) for k in FLAT_KEYS}


def main():
    if len(sys.argv) < 2:
        print("usage: build_ai_section.py <YYYY-MM-DD> [data_root]", file=sys.stderr)
        sys.exit(2)
    date = sys.argv[1]
    data_root = sys.argv[2] if len(sys.argv) > 2 else "frontend/static/data"
    day_dir = os.path.join(data_root, date)
    if not os.path.isdir(day_dir):
        print(f"ERROR: {day_dir} not found", file=sys.stderr)
        sys.exit(1)

    # Collect AI/tech matches across the real sections (cross-list: originals untouched).
    matches = []
    for sec in SECTIONS:
        p = os.path.join(day_dir, f"{sec}.json")
        if not os.path.exists(p):
            continue
        data = json.load(open(p, encoding="utf-8"))
        for it in data.get("items", []):
            if matched_terms(it):
                matches.append(it)

    summary_path = os.path.join(day_dir, "summary.json")
    summary = json.load(open(summary_path, encoding="utf-8"))
    index_path = os.path.join(data_root, "index.json")
    index = json.load(open(index_path, encoding="utf-8")) if os.path.exists(index_path) else None
    ai_path = os.path.join(day_dir, "ai.json")

    if not matches:
        # Hide on empty: remove any stale ai artifacts for this day.
        summary.get("categories", {}).pop("ai", None)
        if os.path.exists(ai_path):
            os.remove(ai_path)
        json.dump(summary, open(summary_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"No AI/tech articles for {date}; AI section hidden.")
        return

    matches.sort(key=lambda x: x.get("importance", 0), reverse=True)

    # Themes for the AI section: the tech concepts actually present today,
    # ordered by how many matched articles touch each (then display priority).
    concept_counts = Counter()
    concept_label = {}
    for it in matches:
        for key, label in concepts_for(it):
            concept_counts[key] += 1
            concept_label[key] = label
    order = [k for k, _, _ in CONCEPTS]
    ranked = sorted(concept_counts, key=lambda k: (-concept_counts[k], order.index(k)))[:4]
    themes = {
        "el": [concept_label[k]["el"] for k in ranked],
        "en": [concept_label[k]["en"] for k in ranked],
    }

    now = datetime.now(timezone.utc).isoformat()
    ai_file = {
        "date": date,
        "generated_at": now,
        "category": "ai",
        "item_count": len(matches),
        "themes": themes,
        # Keep each item's ORIGINAL `category` field so the UI can show provenance.
        "items": matches,
    }
    json.dump(ai_file, open(ai_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # Inject into summary.json with the frontend-required shape.
    summary.setdefault("categories", {})["ai"] = {
        "item_count": len(matches),
        "top_items": [flat(it) for it in matches[:5]],
    }
    json.dump(summary, open(summary_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # Register `ai` in index.available_categories (metadata; harmless if unused).
    if index is not None:
        cats = index.setdefault("available_categories", [])
        if "ai" not in cats:
            cats.append("ai")
            cats.sort()
        index["last_updated"] = now
        json.dump(index, open(index_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"AI section built for {date}: {len(matches)} articles.")
    for it in matches:
        print(f"  [{it.get('category')}] {it.get('importance')} {it.get('title')[:70]}")


if __name__ == "__main__":
    main()
