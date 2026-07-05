"""
telegram_bot.py — Kateqoriyalanmış xəbərləri Telegram-a göndərir.

Mesaj formatı (örnek.md-ə uyğun):
──────────────────────────────────
🤖 Süni İntellekt

📌 OpenAI saniyədə 1000 token yaradan yeni modelini təqdim etdi
📝 OpenAI, GPT modelinin yeni versiyasını elan etdi — bu model əvvəlkilərdən...
🔗 techcrunch.com  •  ⭐ 9/10
[👍 12] [👎 2]  ← Oylama butonları

📌 Anthropic 16 AI agenti ilə C kompilyatoru yazdırdı
📝 ...
──────────────────────────────────
"""

import logging
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CATEGORIES
from ai_processor import group_by_category
from news_memory import assign_batch_ids
from votes import get_vote_counts

logger = logging.getLogger(__name__)

_TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
_MAX_MSG_LEN  = 4000   # Telegram limiti 4096, ehtiyatlı ol


# ─── Köməkçi funksiyalar ──────────────────────────────────────────────────────

def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url


def _send_message(text: str, reply_markup: dict = None, chat_id: str = None) -> bool:
    """Telegram-a bir mesaj göndər (opsiyonel inline keyboard ilə)."""
    try:
        payload = {
            "chat_id":    chat_id or TELEGRAM_CHAT_ID,
            "text":       text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        resp = requests.post(
            f"{_TELEGRAM_API}/sendMessage",
            json=payload,
            timeout=20,
        )
        data = resp.json()
        if not data.get("ok"):
            logger.error("Telegram xəta: %s", data)
            return False
        return True
    except Exception as exc:
        logger.error("Telegram göndərmə xətası: %s", exc)
        return False


def _create_vote_keyboard(article_id: str) -> dict:
    """Oylama üçün inline keyboard yarat."""
    votes = get_vote_counts(article_id)
    up_text = f"👍 {votes['up']}"
    down_text = f"👎 {votes['down']}"
    
    return {
        "inline_keyboard": [
            [
                {"text": up_text, "callback_data": f"vote:{article_id}:up"},
                {"text": down_text, "callback_data": f"vote:{article_id}:down"},
            ]
        ]
    }


# ─── Mesaj formatı ────────────────────────────────────────────────────────────

def _format_category_block(category_key: str, articles: list[dict]) -> list[dict]:
    """
    Bir kateqoriya üçün Telegram mesaj bloku yarat (oylama butonları ilə).
    Returns: [{"text": ..., "keyboard": ...}, ...]
    """
    emoji, label = CATEGORIES[category_key]
    results = []
    
    for art in articles:
        importance = art.get("importance", 0)
        stars = "⭐" * min(importance // 3, 3)
        
        art_id = art["bot_id"]
        
        lines = [f"<b>{emoji} {label}</b>", ""]
        lines.append(f"📌 <b>[{art_id}] {art['title_az']}</b>")
        if art.get("summary_az"):
            lines.append(f"📝 {art['summary_az']}")
        lines.append(
            f"🔗 <a href=\"{art['link']}\">{_domain(art['link'])}</a>"
            + (f"  {stars}" if stars else "")
        )
        
        text = "\n".join(lines)
        keyboard = _create_vote_keyboard(art_id)
        
        results.append({"text": text, "keyboard": keyboard})
    
    return results


def _chunk_messages(blocks: list[dict]) -> list[dict]:
    """Bloklardan Telegram limiti keçməyən mesajlar yarat."""
    messages: list[dict] = []
    current_text = ""
    current_keyboard = None

    for block in blocks:
        candidate_text = (current_text + "\n\n" + block["text"]).strip() if current_text else block["text"]
        if len(candidate_text) > _MAX_MSG_LEN:
            if current_text:
                messages.append({"text": current_text.strip(), "keyboard": current_keyboard})
            current_text = block["text"]
            current_keyboard = block["keyboard"]
        else:
            current_text = candidate_text
            current_keyboard = block["keyboard"]

    if current_text.strip():
        messages.append({"text": current_text.strip(), "keyboard": current_keyboard})

    return messages


def _send_message_batch(messages: list[dict]) -> int:
    """Mesajları paralel olaraq göndər."""
    sent = 0
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_msg = {
            executor.submit(
                _send_message, 
                msg["text"], 
                msg.get("keyboard")
            ): msg
            for msg in messages
        }
        
        for future in as_completed(future_to_msg):
            try:
                if future.result():
                    sent += 1
            except Exception as exc:
                logger.error("Mesaj göndərmə xətası: %s", exc)
    
    return sent


# ─── Əsas funksiyalar ─────────────────────────────────────────────────────────

def send_news_digest(articles: list[dict]) -> int:
    """
    Kateqoriyalanmış xəbərləri Telegram-a göndər (oylama butonları ilə).
    Returns: göndərilmiş mesaj sayı
    """
    if not articles:
        logger.info("Göndəriləcək xəbər yoxdur.")
        return 0

    articles.sort(key=lambda x: x.get("importance", 0), reverse=True)
    
    grouped = group_by_category(articles)

    list_for_ids = []
    for key in CATEGORIES:
        if key in grouped:
            list_for_ids.extend(grouped[key])
            
    assign_batch_ids(list_for_ids)

    blocks: list[dict] = []
    for key in CATEGORIES:
        arts = grouped.get(key, [])
        if arts:
            blocks.extend(_format_category_block(key, arts))

    if not blocks:
        return 0

    # Başlıq mesajı (Bakı vaxtı ilə)
    baku_tz = timezone(timedelta(hours=4))
    now = datetime.now(baku_tz).strftime("%d %B %Y, %H:%M")
    header_text = (
        f"🗞 <b>Texnologiya Xəbərləri</b>\n"
        f"📅 {now} (Bakı vaxtı)\n"
        f"📊 {len(articles)} xəbər — {len(grouped)} kateqoriya\n"
        f"{'─' * 30}\n\n"
        f"💡 Hər xəbərə 👍👎 ilə oy verə bilərsiniz!"
    )
    
    header = {"text": header_text, "keyboard": None}

    messages = [header] + _chunk_messages(blocks)

    # Paralel göndərmə
    sent = _send_message_batch(messages)

    logger.info("Telegram-a %d mesaj göndərildi (oylama ilə).", sent)
    return sent


def send_startup_message() -> None:
    """Bot işə düşəndə test mesajı göndər."""
    from config import MIN_IMPORTANCE_SCORE
    text = (
        "🤖 <b>Texnologiya Xəbər Botu işə düşdü!</b>\n\n"
        "📡 Aktiv mənbələr: <b>28 ədəd</b>\n"
        f"⭐ Minimum əhəmiyyət balı: <b>{MIN_IMPORTANCE_SCORE}/10</b>\n\n"
        "🇺🇿 Azərbaycan texnologiya xəbərləri\n"
        "🔒 Siber güvenlik xəbərləri\n"
        "🤖 Süni intellekt yenilikləri\n\n"
        "İlk tarama /tarama ilə başlayır... 🚀"
    )
    _send_message(text)


def send_error_alert(error_msg: str) -> None:
    """Kritik xəta baş verəndə xəbər ver."""
    text = f"⚠️ <b>Bot xətası:</b>\n<code>{error_msg[:500]}</code>"
    _send_message(text)


def answer_callback_query(callback_id: str, text: str = "") -> bool:
    """Telegram callback query cavabı."""
    try:
        resp = requests.post(
            f"{_TELEGRAM_API}/answerCallbackQuery",
            json={
                "callback_query_id": callback_id,
                "text": text,
                "show_alert": False,
            },
            timeout=10,
        )
        return resp.json().get("ok", False)
    except Exception:
        return False
