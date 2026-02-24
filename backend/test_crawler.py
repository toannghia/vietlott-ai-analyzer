import asyncio
from app.services.crawler import run_daily_crawler
import logging

logging.basicConfig(level=logging.INFO)

async def test_crawler():
    print("Testing Crawler on real Vietlott URL...")
    res = await run_daily_crawler()
    print("Crawler Result:", res)

if __name__ == "__main__":
    asyncio.run(test_crawler())
