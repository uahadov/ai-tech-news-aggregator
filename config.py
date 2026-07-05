"""
config.py — Mərkəzi konfiqurasiya faylı
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _safe_int(env_var: str, default: int) -> int:
    """Environment dəyişənini təhlükəsiz şəkildə int-ə çevir."""
    val = os.getenv(env_var, "")
    if not val:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        logger.warning("⚠️ %s üçün keçərsiz dəyər: '%s', default istifadə olunur: %d", env_var, val, default)
        return default


# ─── Telegram ───────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID: str   = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_WEBHOOK_SECRET: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

# Cavab veriləcək icazə verilən Chat ID-lər (vergül ilə ayrılır)
_allowed_ids_raw: str = os.getenv("ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS: set[str] = {
    cid.strip() for cid in _allowed_ids_raw.split(",") if cid.strip()
}
# TELEGRAM_CHAT_ID həmişə icazəli olsun
if TELEGRAM_CHAT_ID:
    ALLOWED_CHAT_IDS.add(TELEGRAM_CHAT_ID)

# ─── Groq və OpenRouter AI ──────────────────────────────────────
GROQ_API_KEY: str  = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

# Modellər ierarxiyası:
# 1) Llama 3.3 70B (Ən ağıllı, kiçik limit)
# 2) Gemma 3 12B (Orta ağıllı, OpenRouter)
# 3) Llama 3.1 8B (Sürətli, böyük limit)
# 4) Mistral 7B (Ehtiyat üçün pulsuz, OpenRouter)
GROQ_MODEL_1: str    = "llama-3.3-70b-versatile"
OPENROUTER_MODEL_2: str = "google/gemma-3-12b-it:free"
GROQ_MODEL_3: str    = "llama-3.1-8b-instant"
OPENROUTER_MODEL_4: str = "mistralai/mistral-7b-instruct:free"

# Model adları (göstərici üçün)
MODEL_NAMES: dict[str, str] = {
    "groq_1": "Llama 3.3 70B (Groq)",
    "openrouter_2": "Gemma 3 12B (OpenRouter)",
    "groq_3": "Llama 3.1 8B (Groq)",
    "openrouter_4": "Mistral 7B (OpenRouter)",
}

# Default olaraq hansından başladılsın (1-ci model)
GROQ_MODEL: str = GROQ_MODEL_1

# ─── Scheduler ───────────────────────────────────────────────
SCAN_INTERVAL_HOURS: int = _safe_int("SCAN_INTERVAL_HOURS", 6)

# ─── Filtr ───────────────────────────────────────────────────
MIN_IMPORTANCE_SCORE: int = _safe_int("MIN_IMPORTANCE_SCORE", 6)
MAX_ARTICLES_PER_RUN: int = _safe_int("MAX_ARTICLES_PER_RUN", 100)

# ─── AI Parametrləri ────────────────────────────────────────
BATCH_SIZE: int = 15                  # Bir sorğuda neçə xəbər
AI_MAX_TOKENS: int = 2048             # AI output token limiti
ARTICLE_TEXT_MAX_CHARS: int = 15000   # Məqalə mətni üçün max simvol
SIMILARITY_THRESHOLD: float = 0.6     # Dublikat aşkarlama həddi
BATCH_DELAY_SECONDS: int = 15         # Batch'ler arası gözləmə (TPM limiti)

# ─── Seen News ──────────────────────────────────────────────
HOURS_LOOKBACK: int = 24              # Geri baxış pəncərəsi (saat)
MAX_SEEN_ENTRIES: int = 5000          # Seen news max entry
MAX_NEWS_MAP_ENTRIES: int = 200       # News map max entry

# ─── Kateqoriyalar (Azerbaycanca) ───────────────────────────
CATEGORIES = {
    "həftənin_hadisəsi":   ("🔥", "Həftənin Hadisəsi"),
    "süni_intellekt":      ("🤖", "Süni İntellekt"),
    "təhlükəsizlik":       ("🔒", "Təhlükəsizlik"),
    "məxfilik":            ("🕵️", "Məxfilik"),
    "avadanlıq":           ("💻", "Avadanlıq"),
    "açıq_mənbə":          ("🐧", "Açıq Mənbə"),
    "oyun":                ("🎮", "Oyun"),
    "azərbaycan_tech":     ("🇦🇿", "Azərbaycan Texnologiyası"),
    "qeyd_etməyə_dəyər":   ("📰", "Qeyd Etməyə Dəyər Xəbərlər"),
}

CATEGORY_NAMES_FOR_AI = list(CATEGORIES.keys())

# ─── Fayl yolları ────────────────────────────────────────────
SEEN_NEWS_FILE: str = os.path.join(os.path.dirname(__file__), "seen_news.json")
NEWS_MAP_FILE: str  = os.path.join(os.path.dirname(__file__), "news_map.json")
LOG_FILE: str       = os.path.join(os.path.dirname(__file__), "bot.log")

# ─── API Auth ────────────────────────────────────────────────
SCAN_API_KEY: str = os.getenv("SCAN_API_KEY", "")  # /scan endpoint üçün
