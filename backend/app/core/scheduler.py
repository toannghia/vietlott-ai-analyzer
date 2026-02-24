import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.crawler import run_daily_crawler

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def start_scheduler():
    """Builds and starts the APScheduler with predefined cron jobs."""
    # Vietlott draws typically happen around 18:00 - 18:30 VN time
    # We schedule the job at 18:45 every day as a safe margin
    scheduler.add_job(
        run_daily_crawler,
        CronTrigger(hour=18, minute=45, timezone="Asia/Ho_Chi_Minh"),
        id="vietlott_daily_crawler",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started successfully. Cron configured for 18:45 VN time.")

def stop_scheduler():
    """Stops the APScheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully.")
