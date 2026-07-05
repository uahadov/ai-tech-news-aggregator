"""
bulletin.py — Həftəlik Xəbər Bülteni

Hər pazar 09:00-da (Bakı vaxtı) həftənin ən çox oy alan xəbərlərini toplayub
Telegram-a göndərir.

İstifadə:
  - /bulent komandu ilə
  - Avtomatik olaraq (əgər scheduler qurulubsa)
"""

import logging
from datetime import datetime, timezone, timedelta

from telegram_bot import _send_message
from votes import get_top_articles, get_total_votes
from news_memory import load_news_map
from rss_reader import _load_seen

logger = logging.getLogger(__name__)


def send_weekly_bulletin(chat_id: str = None) -> bool:
    """
    Həftəlik bülteni Telegram-a göndər.
    Returns: uğurlu olub-olmadığı
    """
    logger.info("Həftəlik bülten hazırlanır...")

    try:
        # Məlumatları topla
        top_articles = get_top_articles(10)
        votes_stats = get_total_votes()
        news_map = load_news_map()
        seen = _load_seen()

        # Həftə tarixləri
        baku_tz = timezone(timedelta(hours=4))
        now = datetime.now(baku_tz)

        # Bu həftənin bazar ertəsindən bazar gününə qədər
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)

        date_range = f"{week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m.%Y')}"

        # Bülten mətnini hazırla
        text = f"""
📰 <b>HƏFTƏLİK XƏBƏR BÜLTƏNİ</b>
📅 {date_range}

{'─' * 30}
"""

        # Ən çox oy alan xəbərlər
        if top_articles:
            text += "\n🏆 <b>ƏN ÇOX OY ALAN XƏBƏRLƏR:</b>\n\n"

            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

            for i, art in enumerate(top_articles):
                medal = medals[i] if i < len(medals) else f"{i+1}."
                title = art['title'][:50] + "..." if len(art['title']) > 50 else art['title']
                text += f"{medal} <b>[{art['article_id']}] {title}</b>\n"
                text += f"    👍 {art['up']}  👎 {art['down']}  (Net: {art['score']})\n\n"
        else:
            text += "\n🏆 <b>ƏN ÇOX OY ALAN XƏBƏRLƏR:</b>\n\n"
            text += "Hələ heç bir oy yoxdur. Xəbərlərə 👍👎 ilə oy verin!\n\n"

        # Statistika
        text += f"""{'─' * 30}

📊 <b>HƏFTƏLİK STATİSTİKA:</b>
  📰 Toplam xəbər: {len(news_map)}
  👁 Görülmüş xəbər: {len(seen)}
  🔗 Aktiv mənbələr: 28

🗳 <b>OYLAMA STATİSTİKASI:</b>
  Toplam oy: {votes_stats['total_votes']}
  👍 Ümumi: {votes_stats['total_up']}
  👎 Ümumi: {votes_stats['total_down']}
  Oylanmış xəbər: {votes_stats['total_articles']}

{'─' * 30}

💡 <i>Hər xəbərə 👍👎 ilə oy verərək ən maraqlı xəbərləri seçməyə kömək edin!</i>

🤖 <i>AzTech Xəbər Botu tərəfindən hazırlanıb</i>
"""

        # Göndər
        _send_message(text, chat_id=chat_id)

        logger.info("Həftəlik bülten göndərildi.")
        return True

    except Exception as exc:
        logger.error("Bülten göndərmə xətası: %s", exc)
        return False


def is_sunday_0900_baku() -> bool:
    """
    İndi Bakı vaxtı ilə Pazar 09:00-dırmı?
    """
    baku_tz = timezone(timedelta(hours=4))
    now = datetime.now(baku_tz)
    return now.weekday() == 6 and now.hour == 9 and now.minute == 0


def check_and_send_bulletin():
    """
    Əgər Pazar 09:00-dırsa bülteni göndər.
    Webhook handler-da çağırıla bilər.
    """
    if is_sunday_0900_baku():
        logger.info("Pazar 09:00 - Həftəlik bülten vaxtı!")
        send_weekly_bulletin()
