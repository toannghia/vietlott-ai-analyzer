import asyncio
import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from sqlalchemy import select
from app.core.database import async_session
from app.models.draw_result import DrawResult
from app.services.crawler import parse_vietlott_results, fetch_vietlott_html
from app.services.statistics import update_number_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def crawl_all_pages(lottery_type: str = "mega645", max_pages: int = 200):
    if lottery_type == "power655":
        base_url = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-655"
        detail_base = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655"
    else:
        base_url = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-645"
        detail_base = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/mega-6-45"

    async with async_session() as db:
        for p in range(1, max_pages + 1):
            param = "cur_page" if lottery_type == "power655" else "p"
            url = f"{base_url}?{param}={p}&nocatche=1"
            try:
                logger.info(f"Crawling {lottery_type} page {p}...")
                html = await fetch_vietlott_html(url)
                with open("debug_crawl.html", "w") as f:
                    f.write(html)
                soup = BeautifulSoup(html, 'html.parser')
                
                rows = soup.select("table.table-hover tbody tr")
                logger.info(f"Found {len(rows)} rows in table.table-hover tbody tr")
                if not rows:
                    logger.info(f"No more results found on page {p}. Stopping.")
                    break
                
                if "Không tìm thấy" in html:
                    break

                for row in rows:
                    cols = row.select("td")
                    if len(cols) < 2: 
                        logger.warning(f"Row has less than 2 columns: {cols}")
                        continue
                    
                    try:
                        # Period is in the second column (index 1)
                        period_raw = cols[1].get_text(strip=True).replace("#", "")
                        # Some formatting might have leading zeros or spaces
                        period_str = str(int(period_raw)).zfill(5)
                        
                        # Check if exists
                        existing = await db.execute(
                            select(DrawResult).where(
                                (DrawResult.draw_period == period_str) & 
                                (DrawResult.type == lottery_type)
                            )
                        )
                        if existing.scalar_one_or_none():
                            logger.info(f"Period {period_str} already exists. Skipping.")
                            continue
                            
                        # Fetch detail
                        detail_url = f"{detail_base}?id={period_str}&nocatche=1"
                        logger.info(f"Fetching detail from {detail_url}")
                        detail_html = await fetch_vietlott_html(detail_url)
                        data = parse_vietlott_results(detail_html, lottery_type)
                        
                        # VERIFY we got the right period (Vietlott might redirect to latest if ID wrong)
                        if data["draw_period"] != period_str:
                            logger.warning(f"Detail page for {period_str} returned {data['draw_period']}. Likely redirected to latest. Skipping.")
                            continue

                        new_draw = DrawResult(
                            draw_date=data["draw_date"],
                            draw_period=data["draw_period"],
                            numbers=data["numbers"],
                            type=lottery_type,
                            jackpot_won=data["jackpot_won"],
                            jackpot_value=data["jackpot_value"],
                            jackpot_winners=data["jackpot_winners"],
                            jackpot2_value=data.get("jackpot2_value", 0),
                            jackpot2_winners=data.get("jackpot2_winners", 0),
                            first_prize_value=data["first_prize_value"],
                            first_prize_winners=data["first_prize_winners"],
                            second_prize_value=data["second_prize_value"],
                            second_prize_winners=data["second_prize_winners"],
                            third_prize_value=data["third_prize_value"],
                            third_prize_winners=data["third_prize_winners"]
                        )
                        db.add(new_draw)
                        logger.info(f"Added {lottery_type} #{period_str} to session")
                    except Exception as e:
                        logger.error(f"Error processing period {period_raw}: {e}")
                        # If integrity error or other flush error, we might need to rollback
                        await db.rollback()
                
                try:
                    await db.commit()
                    logger.info(f"Committed page {p}")
                except Exception as commit_error:
                    logger.error(f"Commit failed for page {p}: {commit_error}")
                    await db.rollback()
                # Throttling
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Page {p} failed: {e}")
                break
        
        # After all pages, update stats
        await update_number_stats(lottery_type=lottery_type)
        logger.info(f"Finished bulk crawl for {lottery_type}")

if __name__ == "__main__":
    import sys
    l_type = sys.argv[1] if len(sys.argv) > 1 else "mega645"
    asyncio.run(crawl_all_pages(l_type))
