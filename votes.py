"""
votes.py — Xəbər oylama sistemi

İstifadə:
  - Hər xəbərə 👍👎 inline keyboard təklif olunur
  - Oylar votes.json-da saxlanılır
  - /stats komutunda en çox oy alan xəbərlər göstərilir
"""

import json
import logging
import os
from typing import Optional

from config import NEWS_MAP_FILE

logger = logging.getLogger(__name__)

VOTES_FILE = os.path.join(os.path.dirname(__file__), "votes.json")


def _load_votes() -> dict:
    """Oylama verilerini yüklə."""
    try:
        if os.path.exists(VOTES_FILE):
            with open(VOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error("votes.json oxunarkən xəta: %s", e)
    return {}


def _save_votes(votes: dict) -> None:
    """Oylama verilerini yaddaşa yaz."""
    try:
        with open(VOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(votes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("votes.json yazılarkən xəta: %s", e)


def add_vote(article_id: str, user_id: int, vote_type: str) -> Optional[str]:
    """
    Oy əlavə et.
    
    Args:
        article_id: Xəbər ID-si
        user_id: Telegram istifadəçi ID-si
        vote_type: "up" (👍) və ya "down" (👎)
    
    Returns:
        Cavab mesajı və ya None (əgər artıq oy veribsə)
    """
    votes = _load_votes()
    
    if article_id not in votes:
        votes[article_id] = {"up": [], "down": [], "up_count": 0, "down_count": 0}
    
    article_votes = votes[article_id]
    
    # İstifadəçi artıq oy verib mi?
    if user_id in article_votes.get("up", []):
        # Artıq 👍 verib, heç bir şey etmə
        return None
    if user_id in article_votes.get("down", []):
        # Artıq 👍 verib, heç bir şey etmə
        return None
    
    # Oyu qeyd et
    if vote_type == "up":
        article_votes["up"].append(user_id)
        article_votes["up_count"] = article_votes.get("up_count", 0) + 1
    elif vote_type == "down":
        article_votes["down"].append(user_id)
        article_votes["down_count"] = article_votes.get("down_count", 0) + 1
    
    _save_votes(votes)
    
    up = article_votes.get("up_count", 0)
    down = article_votes.get("down_count", 0)
    return f"Oyunuz qeydə alındı! 👍 {up}  👎 {down}"


def get_vote_counts(article_id: str) -> dict:
    """Xəbərin oy sayını qaytar."""
    votes = _load_votes()
    if article_id in votes:
        return {
            "up": votes[article_id].get("up_count", 0),
            "down": votes[article_id].get("down_count", 0),
        }
    return {"up": 0, "down": 0}


def get_top_articles(limit: int = 10) -> list[dict]:
    """
    Ən çox oy alan xəbərləri qaytar.
    
    Returns:
        [{"article_id", "title", "up", "down", "score"}, ...]
    """
    votes = _load_votes()
    news_map = _load_news_map()
    
    results = []
    for article_id, vote_data in votes.items():
        up = vote_data.get("up_count", 0)
        down = vote_data.get("down_count", 0)
        score = up - down  # Net oyu hesabla
        
        # Xəbər başlığını tap
        title = "Naməlum xəbər"
        if article_id in news_map:
            title = news_map[article_id].get("title", title)
        
        results.append({
            "article_id": article_id,
            "title": title,
            "up": up,
            "down": down,
            "score": score,
        })
    
    # Net oya görə sırala
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:limit]


def _load_news_map() -> dict:
    """News map yüklə."""
    try:
        if os.path.exists(NEWS_MAP_FILE):
            with open(NEWS_MAP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def get_total_votes() -> dict:
    """Ümumi oylama statistikası."""
    votes = _load_votes()
    total_up = sum(v.get("up_count", 0) for v in votes.values())
    total_down = sum(v.get("down_count", 0) for v in votes.values())
    total_articles = len(votes)
    
    return {
        "total_up": total_up,
        "total_down": total_down,
        "total_articles": total_articles,
        "total_votes": total_up + total_down,
    }
