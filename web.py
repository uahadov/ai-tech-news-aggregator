"""
web.py — Render.com üçün giriş nöqtəsi və Telegram Webhooku

Bura Telegram-dan mesaj gəldikdə, onu oxuyub cavab verəcək.
İstifadəçi `/tarama` yazarsa -> dərhal axtarışa başlayıb Telegram-a atacaq.
`/script 1`, `/m 1`, `/short 1`, `/deep 1`, `/limit`, `/start`, `/help`, `/stats`, `/bulent` komandaları

Özəlliklər:
  - 👍👎 Oylama sistemi (inline keyboard)
  - 📰 Həftəlik bülten (hər pazar 09:00 Bakı vaxtı)
  - 🔄 Webhook tabanlı (Render free tier uyumlu)
"""

import os
import sys
import threading
import logging
import time
import requests

from flask import Flask, request, jsonify
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_WEBHOOK_SECRET, SCAN_API_KEY, ALLOWED_CHAT_IDS
from news_memory import load_news_map
from ai_content_generator import process_command

# Windows terminalında UTF-8 məcburi et
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Thread safety üçün Lock
_scan_lock = threading.Lock()
_is_scanning = False
_start_time = time.time()


def _do_scan(model_choice: int = 1):
    """Arxa planda tarama aparır."""
    global _is_scanning
    with _scan_lock:
        _is_scanning = True
    try:
        from scheduler import run_scan
        run_scan(model_choice)
    except Exception as e:
        logger.error("Tarama xətası: %s", e)
    finally:
        with _scan_lock:
            _is_scanning = False


def _trigger_scan(chat_id=None, model_choice: int = 1):
    """Tarama artıq gedirmi yoxlayır, getmirsə başladır."""
    global _is_scanning
    
    with _scan_lock:
        scanning = _is_scanning
    
    if chat_id:
        from telegram_bot import _send_message
        if scanning:
            _send_message("⏳ Tarama artıq gedir, bir az gözləyin...", chat_id=chat_id)
            return False
        else:
            from config import MODEL_NAMES
            model_name = MODEL_NAMES.get(f"groq_{model_choice}", f"Model {model_choice}")
            _send_message(f"🚀 Bot oyandı! Tarama başladı ({model_name}). Təxminən 2-3 dəqiqəyə xəbərlər gələcək...", chat_id=chat_id)

    t = threading.Thread(target=_do_scan, args=(model_choice,), daemon=True)
    t.start()
    return True


# ─── Oylama Callback ─────────────────────────────────────────────────────────

def handle_vote_callback(callback_query: dict):
    """Oylama inline button callback-i."""
    from telegram_bot import answer_callback_query
    from votes import add_vote
    
    callback_id = callback_query["id"]
    data = callback_query.get("data", "")
    user_id = callback_query["from"]["id"]
    
    # Data formatı: vote:ARTICLE_ID:up və ya vote:ARTICLE_ID:down
    parts = data.split(":")
    if len(parts) != 3 or parts[0] != "vote":
        answer_callback_query(callback_id, "❌ Keçərsiz əməliyyat")
        return
    
    article_id = parts[1]
    vote_type = parts[2]
    
    if vote_type not in ("up", "down"):
        answer_callback_query(callback_id, "❌ Keçərsiz oy növü")
        return
    
    result = add_vote(article_id, user_id, vote_type)
    
    if result:
        answer_callback_query(callback_id, result)
    else:
        answer_callback_query(callback_id, "Siz artıq bu xəbərə oy vermisiniz")


# ─── Komandalar ──────────────────────────────────────────────────────────────

def handle_article_command(command: str, args: list, chat_id: str = None):
    from telegram_bot import _send_message
    
    if not args:
        _send_message("❌ Zəhmət olmasa xəbər ID-ni qeyd edin. Məsələn: `/m 1`", chat_id=chat_id)
        return
        
    article_id = args[0]
    
    # Model seçimini yoxlayaq
    model_choice = 1
    extra_args = ""
    
    if len(args) > 1:
        if args[-1] in ["1", "2", "3"]:
            model_choice = int(args[-1])
            extra_args = " ".join(args[1:-1])
        else:
            extra_args = " ".join(args[1:])
    
    news_map = load_news_map()
    if article_id not in news_map:
        _send_message(f"❌ Təəssüf ki, [{article_id}] nömrəli xəbər yaddaşdan silinib və ya mövcud deyil. Zəhmət olmasa yeni /tarama edin.", chat_id=chat_id)
        return
        
    article_info = news_map[article_id]
    from config import MODEL_NAMES
    model_name = MODEL_NAMES.get(f"groq_{model_choice}", f"Model {model_choice}")
    
    if command == "ask":
        question = extra_args if extra_args else "?"
        _send_message(f"💬 Sualınız işlənir... [{article_id}] \"{question[:50]}\"", chat_id=chat_id)
    else:
        _send_message(f"⏳ [{article_id}] nömrəli xəbər yaradılır ({model_name})...", chat_id=chat_id)
    
    def process_and_send():
        result = process_command(command, article_info, extra_args, article_id, model_choice)
        if len(result) > 4000:
            for i in range(0, len(result), 4000):
                _send_message(result[i:i+4000], chat_id=chat_id)
        else:
            _send_message(result, chat_id=chat_id)
            
    threading.Thread(target=process_and_send, daemon=True).start()


def handle_limit_command(chat_id: str = None):
    from telegram_bot import _send_message
    from usage_memory import load_stats
    from config import MODEL_NAMES
    
    s = load_stats()
    
    text = f"""
📊 <b>API Canlı Limit Vəziyyəti</b>

1️⃣ <b>{MODEL_NAMES['groq_1']}</b>
- Qalan Sorğu: {s.get('groq_1', {}).get('remaining_req', 'N/A')}
- Qalan Token: {s.get('groq_1', {}).get('remaining_tokens', 'N/A')}
- Sıfırlanma: {s.get('groq_1', {}).get('reset_in', 'N/A')}
- Yenilənmə: {s.get('groq_1', {}).get('last_update', 'N/A')}

2️⃣ <b>{MODEL_NAMES['openrouter_2']}</b>
- Status: {s.get('openrouter_2', {}).get('status', 'Məlumat yoxdur')}
- Yenilənmə: {s.get('openrouter_2', {}).get('last_update', 'N/A')}

3️⃣ <b>{MODEL_NAMES['groq_3']}</b>
- Qalan Sorğu: {s.get('groq_3', {}).get('remaining_req', 'N/A')}
- Qalan Token: {s.get('groq_3', {}).get('remaining_tokens', 'N/A')}
- Sıfırlanma: {s.get('groq_3', {}).get('reset_in', 'N/A')}
- Yenilənmə: {s.get('groq_3', {}).get('last_update', 'N/A')}

<i>* "N/A" yazanlar o deməkdir ki, bot fəaliyyətə başlayandan bəri o model hələ işlədilməyib.</i>
"""
    _send_message(text, chat_id=chat_id)


def handle_start_command(chat_id: str = None):
    """Başlanğıc mesajı göndər."""
    from telegram_bot import _send_message

    text = """
🤖 <b>AzTech Xəbər Botu</b>

Salam! Mən Azərbaycan dilində texnologiya xəbərlərini toplayan botam.

<b>Mövcud Komandalar:</b>

📰 <b>/tarama</b> — Yeni xəbərləri tarayır (Model 1: Llama 70B)
📰 <b>/tarama2</b> — Tarama (Model 2: Gemma 12B)
📰 <b>/tarama3</b> — Tarama (Model 3: Llama 8B)

🎬 <b>/script &lt;id&gt; [saniyə]</b> — YouTube/TikTok ssenarisi yarat
📱 <b>/short &lt;id&gt;</b> — Qısa Instagram/Telegram postu
📊 <b>/deep &lt;id&gt;</b> — Dərin analiz
📝 <b>/m &lt;id&gt;</b> — Ssenari (script ilə eyni)
💬 <b>/ask &lt;id&gt; &lt;sual&gt;</b> — Xəbər haqqında sual ver

📰 <b>/bulent</b> — Həftəlik bülten
🔧 <b>/limit</b> — API limitlərini göstər
📊 <b>/stats</b> — Bot statistikası
❓ <b>/help</b> — Bu mesaj

<b Kateqoriyalar:</b>
🔥 Həftənin Hadisəsi | 🤖 Süni İntellekt | 🔒 Təhlükəsizlik
🕵️ Məxfilik | 💻 Avadanlıq | 🐧 Açıq Mənbə | 🎮 Oyun
🇦🇿 Azərbaycan Texnologiyası

💡 <i>Hər xəbərə 👍👎 ilə oy verə bilərsiniz!</i>
"""
    _send_message(text, chat_id=chat_id)


def handle_help_command(chat_id: int):
    """Kömək mesajı göndər."""
    handle_start_command(chat_id)


def handle_stats_command(chat_id: str = None):
    """Bot statistikasını göndər."""
    from telegram_bot import _send_message
    from news_memory import load_news_map
    from rss_reader import _load_seen
    from votes import get_top_articles, get_total_votes
    
    news_map = load_news_map()
    seen = _load_seen()
    uptime = time.time() - _start_time
    votes_stats = get_total_votes()
    top_articles = get_top_articles(5)
    
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    
    top_text = ""
    if top_articles:
        for i, art in enumerate(top_articles, 1):
            top_text += f"  {i}. [{art['article_id']}] {art['title'][:40]}... 👍{art['up']} 👎{art['down']}\n"
    else:
        top_text = "  Hələ heç bir oy yoxdur."
    
    text = f"""
📊 <b>Bot Statistikası</b>

⏱ <b>İşləmə müddəti:</b> {hours} saat {minutes} dəqiqə
📰 <b>Yaddaşdakı xəbərlər:</b> {len(news_map)} ədəd
👁 <b>Görülmüş xəbərlər:</b> {len(seen)} ədəd
🔗 <b>Aktiv mənbələr:</b> 28 ədəd

🗳 <b>Oylama Statistikası:</b>
  Toplam oy: {votes_stats['total_votes']}
  👍 Ümumi: {votes_stats['total_up']}
  👎 Ümumi: {votes_stats['total_down']}
  Oylanmış xəbər: {votes_stats['total_articles']}

🏆 <b>Ən Çox Oy Alan Xəbərlər:</b>
{top_text}
"""
    _send_message(text, chat_id=chat_id)


def handle_bulent_command(chat_id: str = None):
    """Həftəlik bülteni göndər."""
    from telegram_bot import _send_message
    
    _send_message("📰 Həftəlik bülten hazırlanır...", chat_id=chat_id)
    
    def send_bulent():
        from bulletin import send_weekly_bulletin
        send_weekly_bulletin(chat_id)
    
    threading.Thread(target=send_bulent, daemon=True).start()


# ─── Endpoint-lər ────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Render daxil olduqda (Wake up url)"""
    return "Bot oyaqdır və Webhook dinləyir!", 200


@app.route("/health")
def health():
    """Health check endpoint - API bağlantılarını yoxlayır"""
    from config import GROQ_API_KEY, OPENROUTER_API_KEY
    
    checks = {
        "telegram": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        "groq": bool(GROQ_API_KEY),
        "openrouter": bool(OPENROUTER_API_KEY),
        "scanning": _is_scanning,
        "uptime_seconds": int(time.time() - _start_time),
    }
    
    all_ok = all([checks["telegram"], checks["groq"]])
    
    return jsonify({
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
    }), 200 if all_ok else 503


@app.route("/scan")
def scan():
    """Url üzərindən tarama başlat (Auth tələb olunur)"""
    # Auth yoxlaması
    if SCAN_API_KEY:
        api_key = request.args.get("key", "")
        if api_key != SCAN_API_KEY:
            return jsonify({"status": "unauthorized", "message": "Invalid API key"}), 401
    
    started = _trigger_scan()
    if started:
        return jsonify({"status": "started", "message": "Tarama başladı!"})
    return jsonify({"status": "already_running"}), 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """Telegram buraya mesajları göndərəcək (Secret Token yoxlaması ilə)"""
    
    # Telegram Secret Token yoxlaması
    if TELEGRAM_WEBHOOK_SECRET:
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret_token != TELEGRAM_WEBHOOK_SECRET:
            logger.warning("Keçərsiz webhook secret token!")
            return "ok", 200
    
    update = request.get_json(silent=True)
    if not update:
        return "ok", 200
    
    # Callback query (oylama butonları)
    if "callback_query" in update:
        handle_vote_callback(update["callback_query"])
        return "ok", 200
    
    # Mesaj yoxlaması
    if "message" not in update or "text" not in update.get("message", {}):
        return "ok", 200
    
    text = update["message"]["text"].lower()
    chat_id = update["message"]["chat"]["id"]
    
    # Təhlükəsizlik: İcazə verilməmiş chat ID-lərdən gəlməyən mesajları rədd et
    if str(chat_id) not in ALLOWED_CHAT_IDS:
        logger.warning("İcazəsiz giriş cəhdi (Chat ID: %s): %s", chat_id, text)
        return "ok", 200
    
    # Chat ID-ni string formatına çevir (cavab göndərmək üçün)
    chat_id_str = str(chat_id)
        
    parts = text.split()
    command = parts[0]
    args = parts[1:]
    
    if command in ["/start", "/help"]:
        logger.info("%s əmri gəldi (Chat: %s)", command, chat_id)
        handle_start_command(chat_id_str)
        
    elif command in ["/tarama", "/tarama1", "/tarama2", "/tarama3"]:
        model_choice = 1
        if command == "/tarama2": model_choice = 2
        elif command == "/tarama3": model_choice = 3
        
        logger.info("Telegram-dan %s əmri gəldi (Seçim: %d)", command, model_choice)
        _trigger_scan(chat_id=chat_id_str, model_choice=model_choice)
        
    elif command in ["/m", "/script", "/short", "/deep", "/ask", "/chat"]:
        cmd_type = "script" if command == "/m" else command[1:]
        if command == "/chat":
            cmd_type = "ask"
        handle_article_command(cmd_type, args, chat_id_str)
        
    elif command == "/limit":
        handle_limit_command(chat_id_str)
        
    elif command == "/stats":
        handle_stats_command(chat_id_str)
        
    elif command == "/bulent":
        handle_bulent_command(chat_id_str)
        
    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Flask server başladı -> port %d", port)
    app.run(host="0.0.0.0", port=port, debug=False)
