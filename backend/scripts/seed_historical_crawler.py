import asyncio
import httpx
from bs4 import BeautifulSoup
import re
from datetime import datetime
import sys
import os

# add parent dir to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.models.draw_result import DrawResult

async def fetch_draw_html(client, period: int):
    # Parameterized URL that works reliably
    url = f"https://www.vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645?id={period:05d}&nocatche=1"
    try:
        response = await client.get(url, timeout=10.0)
        return response.text
    except Exception as e:
        print(f"Failed to fetch period {period}: {e}")
        return None

def parse_vietlott_results(html: str, period: int) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    try:
        header = soup.select_one(".chitietketqua_title")
        if not header:
            return None
            
        h5 = header.select_one("h5")
        if not h5:
            return None
            
        # Extract period and date: "Kỳ quay thưởng #01475 ngày 22/02/2026"
        m = re.search(r"#(\d+).*?(\d{2}/\d{2}/\d{4})", h5.text)
        if not m:
            return None
            
        draw_date = datetime.strptime(m.group(2), "%d/%m/%Y").date()
        
        nums = [int(n.text.strip()) for n in soup.select(".day_so_ket_qua_v2 span") if n.text.strip().isdigit()]
        if len(nums) < 6:
            return None
            
        # Prize parsing
        jackpot_value = 0
        jackpot_winners = 0
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
                
                if "Jackpot" in prize_name:
                    jackpot_value = val
                    jackpot_winners = winners
                elif "Nhất" in prize_name:
                    first_prize_value = val
                    first_prize_winners = winners
                elif "Nhì" in prize_name:
                    second_prize_value = val
                    second_prize_winners = winners
                elif "Ba" in prize_name:
                    third_prize_value = val
                    third_prize_winners = winners

        return {
            "draw_period": period,
            "draw_date": draw_date,
            "numbers": nums[:6],
            "jackpot_value": jackpot_value,
            "jackpot_winners": jackpot_winners,
            "jackpot_won": jackpot_winners > 0,
            "first_prize_value": first_prize_value,
            "first_prize_winners": first_prize_winners,
            "second_prize_value": second_prize_value,
            "second_prize_winners": second_prize_winners,
            "third_prize_value": third_prize_value,
            "third_prize_winners": third_prize_winners,
        }
    except Exception as e:
        print(f"Error parsing period {period}: {e}")
        return None

async def main():
    start_period = 1
    end_period = 1475 # Crawl ALL 1475 periods requested by user
    
    print(f"Crawling ALL historical Mega 6/45 data from period {end_period} down to {start_period}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    async with httpx.AsyncClient(headers=headers, verify=False) as client:
        async with async_session() as db:
            for p in range(end_period, start_period - 1, -1):
                html = await fetch_draw_html(client, p)
                if not html:
                    continue
                
                data = parse_vietlott_results(html, p)
                if data:
                    print(f"Parsed {p}: {data['draw_date']} - {data['numbers']}")
                    new_draw = DrawResult(
                        draw_date=data["draw_date"],
                        draw_period=str(data["draw_period"]),
                        numbers=data["numbers"],
                        type="mega645",
                        jackpot_won=data["jackpot_won"],
                        jackpot_value=data["jackpot_value"],
                        jackpot_winners=data["jackpot_winners"],
                        first_prize_value=data["first_prize_value"],
                        first_prize_winners=data["first_prize_winners"],
                        second_prize_value=data["second_prize_value"],
                        second_prize_winners=data["second_prize_winners"],
                        third_prize_value=data["third_prize_value"],
                        third_prize_winners=data["third_prize_winners"],
                        raw_html_log="Historical Seed"
                    )
                    
                    try:
                        db.add(new_draw)
                        await db.commit()
                        print(f" -> Saved {p} to DB")
                    except Exception as e:
                        await db.rollback()
                        print(f" -> DB Error on {p} (maybe already exists)")
                else:
                    print(f"No valid data parsed for {p}")
                
                await asyncio.sleep(0.1) # Faster crawl

if __name__ == "__main__":
    asyncio.run(main())
