import json
import logging
import os
from config import NEWS_MAP_FILE, MAX_NEWS_MAP_ENTRIES

logger = logging.getLogger(__name__)

def load_news_map() -> dict:
    """Yaddaşdan ID -> Xəbər xəritəsini yükləyir."""
    try:
        if os.path.exists(NEWS_MAP_FILE):
            with open(NEWS_MAP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error("news_map.json oxunarkən xəta: %s", e)
    return {}

def save_news_map(news_map: dict) -> None:
    """ID -> Xəbər xəritəsini yaddaşa yazır."""
    try:
        if len(news_map) > MAX_NEWS_MAP_ENTRIES:
            keys_to_keep = list(news_map.keys())[-MAX_NEWS_MAP_ENTRIES:]
            news_map = {k: news_map[k] for k in keys_to_keep}
            
        with open(NEWS_MAP_FILE, "w", encoding="utf-8") as f:
            json.dump(news_map, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("news_map.json yazılarkən xəta: %s", e)

def assign_batch_ids(articles: list[dict]) -> None:
    """Xəbərlərə 1-dən başlayaraq seqvential ID-lər təyin edir və yaddaşa yazır."""
    news_map = load_news_map()
    
    for idx, article in enumerate(articles):
        str_id = str(idx + 1)
        news_map[str_id] = {
            "title": article.get("title_az", article.get("title", "")),
            "link": article.get("link", ""),
            "source": article.get("source", ""),
        }
        article["bot_id"] = str_id
        
    save_news_map(news_map)
