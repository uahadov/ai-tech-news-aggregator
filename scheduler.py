"""
scheduler.py — APScheduler ilə avtomatik tarama.

Graceful Shutdown dəstəyi:
  - SIGTERM siqnalı (Docker/Render) üçün handler
  - SIGINT (Ctrl+C) üçün handler
"""

import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import SCAN_INTERVAL_HOURS

logger = logging.getLogger(__name__)

# Global scheduler reference (signal handler üçün)
_scheduler = None


def run_scan(model_choice: int = 1) -> None:
    """Bir tarama dövrü: RSS → AI → Telegram."""
    from rss_reader  import fetch_new_articles
    from ai_processor import process_articles
    from telegram_bot import send_news_digest, send_error_alert

    logger.info("═" * 50)
    logger.info("Tarama başladı (Seçim: %d)...", model_choice)

    try:
        # 1) Yeni xəbərləri yığ
        articles = fetch_new_articles()
        if not articles:
            logger.info("Yeni xəbər tapılmadı. Tarama tamamlandı.")
            return

        # 2) AI ilə emal et (kateqorizasiya + Azerbaycancaya çevir)
        processed = process_articles(articles, model_choice)
        if not processed:
            logger.info("Filtrdən keçən xəbər yoxdur.")
            return

        # 3) Telegram-a göndər
        sent = send_news_digest(processed)
        logger.info("Tarama tamamlandı. Göndərilən mesaj: %d", sent)

    except Exception as exc:
        logger.exception("Tarama zamanı xəta: %s", exc)
        try:
            send_error_alert(str(exc))
        except Exception:
            pass

    logger.info("═" * 50)


def _shutdown_handler(signum, frame):
    """Graceful shutdown handler."""
    global _scheduler
    sig_name = signal.Signals(signum).name
    logger.info("Siqnal alındı: %s — Scheduler dayandırılır...", sig_name)
    
    if _scheduler:
        _scheduler.shutdown(wait=False)
    
    logger.info("Bot dayandırıldı.")
    sys.exit(0)


def start_scheduler() -> None:
    """Scheduler-i işə sal — proqram burada bloklanır."""
    global _scheduler
    
    _scheduler = BlockingScheduler(timezone="UTC")

    _scheduler.add_job(
        func=run_scan,
        trigger=IntervalTrigger(hours=SCAN_INTERVAL_HOURS),
        id="news_scan",
        name="Tech Xəbər Taraması",
        max_instances=1,
        misfire_grace_time=300,
    )

    # Siqnal handler-ları qur
    signal.signal(signal.SIGTERM, _shutdown_handler)
    signal.signal(signal.SIGINT, _shutdown_handler)

    logger.info(
        "Scheduler başladı — hər %d saatdan bir tarama aparılacaq.",
        SCAN_INTERVAL_HOURS,
    )

    try:
        _scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler dayandırıldı.")
        _scheduler.shutdown()
