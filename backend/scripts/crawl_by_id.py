import asyncio
import logging
from sqlalchemy import select
from app.core.database import async_session
from app.models.draw_result import DrawResult
from app.services.crawler import parse_vietlott_results, fetch_vietlott_html
from app.services.statistics import update_number_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def crawl_range(lottery_type: str, start_id: int, end_id: int):
    detail_base = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655" if lottery_type == "power655" else "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/mega-6-45"
    
    async with async_session() as db:
        for i in range(start_id, end_id - 1, -1):
            period_str = str(i).zfill(5)
            
            # Check if exists
            existing = await db.execute(
                select(DrawResult).where(
                    (DrawResult.draw_period == period_str) & 
                    (DrawResult.type == lottery_type)
                )
            )
            if existing.scalar_one_or_none():
                # logger.info(f"Period {period_str} already exists. Skipping.")
                continue
                
            url = f"{detail_base}?id={period_str}&nocatche=1"
            try:
                html = await fetch_vietlott_html(url)
                if not html or "không tìm thấy" in html.lower():
                    logger.warning(f"Period {period_str} not found. Skipping.")
                    continue
                    
                data = parse_vietlott_results(html, lottery_type)
                if data["draw_period"] != period_str:
                    # Vietlott redirects to latest if ID invalid
                    logger.warning(f"Requested {period_str} but got {data['draw_period']}. Skipping.")
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
                logger.info(f"Added {lottery_type} #{period_str}")
                
                # Commit every 20 records to avoid huge transactions
                if i % 20 == 0:
                    await db.commit()
                    
                await asyncio.sleep(1.0) # Throttling
                
            except Exception as e:
                logger.error(f"Error crawling {period_str}: {e}")
                await db.rollback()
                
        await db.commit()
    
    # After all crawling, update stats
    async with async_session() as db:
        await update_number_stats(lottery_type)
    logger.info(f"Finished crawling and updated stats for {lottery_type}")

if __name__ == "__main__":
    import sys
    ltype = sys.argv[1] if len(sys.argv) > 1 else "power655"
    sid = int(sys.argv[2]) if len(sys.argv) > 2 else 1310
    eid = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    asyncio.run(crawl_range(ltype, sid, eid))
