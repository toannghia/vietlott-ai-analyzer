import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.draw_result import DrawResult
from app.services.telegram import send_telegram_alert
from app.services.statistics import update_number_stats
from app.services.ai_service import generate_prediction, verify_prediction

logger = logging.getLogger(__name__)

async def fetch_vietlott_html(url: str) -> str:
    """Fetch raw HTML from Vietlott site using curl to bypass detection."""
    import subprocess
    try:
        # Use curl directly as it bypasses the silent pagination redirection/blocking
        cmd = [
            "curl", "-s", "-L",
            "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            url
        ]
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: subprocess.run(cmd, capture_output=True, text=True))
        if result.returncode != 0:
            logger.error(f"Curl failed for {url}: {result.stderr}")
            return ""
        return result.stdout
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return ""

def parse_vietlott_results(html: str, lottery_type: str = "mega645") -> Dict:
    """Parse HTML using BeautifulSoup to extract latest 6/45 or 6/55 results."""
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        header = soup.select_one(".chitietketqua_title")
        if not header:
            raise ValueError("Could not find title header")
            
        h5 = header.select_one("h5")
        if not h5:
            raise ValueError("Could not find h5 in title header")
            
        import re
        m = re.search(r"#(\d+).*?(\d{2}/\d{2}/\d{4})", h5.text)
        if not m:
            raise ValueError("Could not parse period and date from title")
            
        draw_period = int(m.group(1))
        draw_date = datetime.strptime(m.group(2), "%d/%m/%Y").date()
        
        nums = [int(n.text.strip()) for n in soup.select(".day_so_ket_qua_v2 span") if n.text.strip().isdigit()]
        min_nums = 7 if lottery_type == "power655" else 6
        if len(nums) < min_nums:
            raise ValueError(f"Could not parse {min_nums} winning numbers for {lottery_type}")
            
        # Prize parsing
        jackpot_value = 0
        jackpot_winners = 0
        jackpot2_value = 0
        jackpot2_winners = 0
        first_prize_value = 0
        first_prize_winners = 0
        second_prize_value = 0
        second_prize_winners = 0
        third_prize_value = 0
        third_prize_winners = 0
        
        for row in soup.select("table.table-hover tbody tr"):
            cols = row.select("td")
            if cols and len(cols) > 3:
                prize_name = cols[0].text.strip()
                winners_str = cols[2].text.strip()
                prize_val_str = cols[3].text.strip()
                
                val = int("".join(c for c in prize_val_str if c.isdigit()) or 0)
                winners = int("".join(c for c in winners_str if c.isdigit()) or 0)
                
                if lottery_type == "power655":
                    if "Jackpot 1" in prize_name:
                        jackpot_value = val
                        jackpot_winners = winners
                    elif "Jackpot 2" in prize_name:
                        jackpot2_value = val
                        jackpot2_winners = winners
                else:
                    if "Jackpot" in prize_name:
                        jackpot_value = val
                        jackpot_winners = winners
                
                if "Nhất" in prize_name:
                    first_prize_value = val
                    first_prize_winners = winners
                elif "Nhì" in prize_name:
                    second_prize_value = val
                    second_prize_winners = winners
                elif "Ba" in prize_name:
                    third_prize_value = val
                    third_prize_winners = winners

        return {
            "draw_period": f"{draw_period:05d}",
            "draw_date": draw_date,
            "numbers": nums,
            "jackpot_value": jackpot_value,
            "jackpot_winners": jackpot_winners,
            "jackpot2_value": jackpot2_value,
            "jackpot2_winners": jackpot2_winners,
            "jackpot_won": (jackpot_winners + jackpot2_winners) > 0,
            "first_prize_value": first_prize_value,
            "first_prize_winners": first_prize_winners,
            "second_prize_value": second_prize_value,
            "second_prize_winners": second_prize_winners,
            "third_prize_value": third_prize_value,
            "third_prize_winners": third_prize_winners,
        }
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        raise ValueError(f"Failed to parse Vietlott HTML structure: {e}")
        
async def run_daily_crawler(lottery_type: str = "mega645") -> bool:
    """Main crawler entrypoint scheduled daily."""
    if lottery_type == "power655":
        url = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655"
    else:
        url = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/mega-6-45"
        
    html = ""
    try:
        logger.info(f"Starting crawler for {url} ({lottery_type})")
        html = await fetch_vietlott_html(url)
        data = parse_vietlott_results(html, lottery_type)
        
        async with async_session() as db:
            # Check if this period already exists
            existing = await db.execute(
                select(DrawResult).where(
                    (DrawResult.draw_period == data["draw_period"]) & 
                    (DrawResult.type == lottery_type)
                )
            )
            if existing.scalar_one_or_none():
                logger.info(f"Draw period {data['draw_period']} ({lottery_type}) already exists in DB. Refreshing stats.")
                await update_number_stats(lottery_type=lottery_type)
                return True
                
            new_draw = DrawResult(
                draw_date=data["draw_date"],
                draw_period=str(data["draw_period"]),
                numbers=data["numbers"],
                type=lottery_type,
                jackpot_won=data["jackpot_won"],
                jackpot_value=data["jackpot_value"],
                jackpot_winners=data.get("jackpot_winners", 0),
                jackpot2_value=data.get("jackpot2_value", 0),
                jackpot2_winners=data.get("jackpot2_winners", 0),
                first_prize_value=data.get("first_prize_value", 0),
                first_prize_winners=data.get("first_prize_winners", 0),
                second_prize_value=data.get("second_prize_value", 0),
                second_prize_winners=data.get("second_prize_winners", 0),
                third_prize_value=data.get("third_prize_value", 0),
                third_prize_winners=data.get("third_prize_winners", 0),
                raw_html_log=html
            )
            db.add(new_draw)
            await db.commit()
            
            # TRIGGER STATISTICS UPDATE for specific type
            await update_number_stats(lottery_type=lottery_type)
            
            # VERIFY PREVIOUS AI PREDICTION for this draw period
            await verify_prediction(data["draw_period"], data["numbers"], lottery_type=lottery_type)
            
            # GENERATE AI PREDICTION FOR NEXT PERIOD
            try:
                next_period_int = int(data['draw_period']) + 1
                next_period = f"{next_period_int:05d}"
            except ValueError:
                next_period = data['draw_period'] + "_next"
            await generate_prediction(next_period, lottery_type=lottery_type)
            
            logger.info(f"Successfully scraped and saved {lottery_type} draw period {data['draw_period']}")
            return True

    except Exception as e:
        error_msg = f"Crawler failed for {url}: {str(e)}"
        logger.error(error_msg)
        await send_telegram_alert(error_msg)
        return False
