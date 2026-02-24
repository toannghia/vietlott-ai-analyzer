import logging
import httpx
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def send_telegram_alert(message: str) -> None:
    """Send an alert message to the configured Telegram chat."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram bot token or chat ID is not configured. Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": f"🚨 *Vietlott Analyzer Alert* 🚨\n\n{message}",
        "parse_mode": "Markdown"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info("Successfully sent Telegram alert.")
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
