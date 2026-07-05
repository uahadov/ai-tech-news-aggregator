import json
import os
import logging

STATS_FILE = "api_usage.json"
logger = logging.getLogger(__name__)

def update_stats(provider: str, headers: dict) -> None:
    """API cavablarından limit məlumatlarını çıxarır və saxlayır."""
    stats = load_stats()
    
    if provider.startswith("groq"):
        stats[provider] = {
            "remaining_req": headers.get("x-ratelimit-remaining-requests", "N/A"),
            "remaining_tokens": headers.get("x-ratelimit-remaining-tokens", "N/A"),
            "reset_in": headers.get("x-ratelimit-reset-requests", "N/A"),
            "last_update": headers.get("date", "N/A"),
        }
    elif provider.startswith("openrouter"):
        stats[provider] = {
            "status": "Aktiv (Son call uğurlu)",
            "last_update": headers.get("date", "N/A"),
        }
        
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logger.error("Limit stats yazıla bilmədi: %s", e)

def load_stats() -> dict:
    """Yaddaşdan statistikaları yükləyir."""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "groq" in data:
                    data = {}
                else:
                    return data
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "groq_1": {"remaining_req": "N/A", "remaining_tokens": "N/A", "reset_in": "N/A", "last_update": "N/A"},
        "openrouter_2": {"status": "Məlumat yoxdur", "last_update": "N/A"},
        "groq_3": {"remaining_req": "N/A", "remaining_tokens": "N/A", "reset_in": "N/A", "last_update": "N/A"},
        "openrouter_4": {"status": "Məlumat yoxdur", "last_update": "N/A"},
    }
