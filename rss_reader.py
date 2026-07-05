"""
rss_reader.py — RSS mənbələrindən yeni xəbərləri oxuyur.

Xüsusiyyətlər:
  - Artıq göndərilmiş xəbərlər seen_news.json-da saxlanılır (dublikat yoxdur)
  - Yalnız son HOURS_LOOKBACK saat içindəki xəbərlər götürülür
  - MAX_ARTICLES_PER_RUN həddinə görə ən yeni xəbərlər seçilir
  - Paralel yükləmə ilə sürətli işləmə
"""

import json
import logging
import hashlib
import re
import time
import requests
from datetime import datetime, timezone, timedelta
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser

from config import (
    SEEN_NEWS_FILE,
    MAX_ARTICLES_PER_RUN,
    HOURS_LOOKBACK,
    MAX_SEEN_ENTRIES,
)
from feeds import RSS_FEEDS

logger = logging.getLogger(__name__)


# ─── Seen news yüklə / saxla ──────────────────────────────────────────────────

def _load_seen() -> set[str]:
    try:
        with open(SEEN_NEWS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def _save_seen(seen: set[str]) -> None:
    try:
        seen_list = list(seen)[-MAX_SEEN_ENTRIES:]
        with open(SEEN_NEWS_FILE, "w", encoding="utf-8") as f:
            json.dump(seen_list, f)
    except Exception as e:
        logger.error("Seen news saxlanarkən xəta: %s", e)


def _make_id(entry: Any) -> str:
    """Xəbər üçün unikal ID yarat (URL və ya hash)."""
    raw = getattr(entry, "link", "") or getattr(entry, "id", "") or entry.get("title", "")
    return hashlib.md5(raw.encode()).hexdigest()


def _parse_date(entry: Any) -> datetime | None:
    """feedparser struct_time → datetime (UTC)."""
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _clean_html(text: str) -> str:
    """HTML taglarını təmizlə."""
    text = re.sub(r"<[^>]+>", " ", text).strip()
    return " ".join(text.split())[:400]


# ─── Tək feed yükləmə ─────────────────────────────────────────────────────────

def _fetch_single_feed(feed_info: dict, cutoff: datetime, seen: set[str]) -> list[dict]:
    """Tək bir RSS feed-dən yeni xəbərləri yüklə."""
    url = feed_info["url"]
    name = feed_info["name"]
    hint = feed_info.get("hint")
    collected = []

    try:
        resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; TechNewsBot/2.0)"},
        )
        resp.raise_for_status()
        d = feedparser.parse(resp.text)
    except Exception as exc:
        logger.warning("RSS yüklənmədi: %s — %s", name, exc)
        return []

    for entry in d.entries:
        art_id = _make_id(entry)
        if art_id in seen:
            continue

        pub = _parse_date(entry)
        if pub is None:
            continue
        if pub < cutoff:
            continue

        title = getattr(entry, "title", "").strip()
        if not title:
            continue

        summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
        summary = _clean_html(summary)

        collected.append({
            "id":          art_id,
            "title":       title,
            "description": summary,
            "link":        getattr(entry, "link", url),
            "source":      name,
            "hint":        hint,
            "published":   pub.isoformat() if pub else None,
        })

    return collected


# ─── Əsas funksiya ────────────────────────────────────────────────────────────

def fetch_new_articles() -> list[dict]:
    """
    Bütün RSS mənbələrindən yeni xəbərləri yığır (paralel yükləmə ilə).
    Returns: [{"title", "description", "link", "source", "hint", "published"}]
    """
    seen = _load_seen()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)

    collected: list[dict] = []

    # Paralel yükləmə
    max_workers = min(len(RSS_FEEDS), 8)  # Eyni anda maksimum 8 feed
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_feed = {
            executor.submit(_fetch_single_feed, feed_info, cutoff, seen): feed_info
            for feed_info in RSS_FEEDS
        }

        for future in as_completed(future_to_feed):
            feed_info = future_to_feed[future]
            try:
                articles = future.result()
                collected.extend(articles)
            except Exception as exc:
                logger.error("Feed yükləmə xətası (%s): %s", feed_info["name"], exc)

    # Ən yenilərini öndə saxla, MAX_ARTICLES_PER_RUN ilə kəs
    collected.sort(key=lambda x: x["published"] or "", reverse=True)
    collected = collected[:MAX_ARTICLES_PER_RUN]

    logger.info("Yeni xəbər: %d (mənbə: %d)", len(collected), len(RSS_FEEDS))

    # Görülmüşlər siyahısını yenilə
    new_ids = {a["id"] for a in collected}
    seen.update(new_ids)
    _save_seen(seen)

    return collected
