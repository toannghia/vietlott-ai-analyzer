import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime

with open("test3.html") as f:
    soup = BeautifulSoup(f, "html.parser")

    header = soup.select_one(".chitietketqua_title")
    if header:
        h5 = header.select_one("h5")
        if h5:
            text = h5.text
            import re
            m = re.search(r"#(\d+).*?(\d{2}/\d{2}/\d{4})", text)
            if m:
                period = int(m.group(1))
                date_str = m.group(2)
                draw_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                print("Parsed period:", period, "date:", draw_date)

    nums = [int(n.text.strip()) for n in soup.select(".day_so_ket_qua_v2 span") if n.text.strip().isdigit()]
    print("Numbers:", nums)
    
    jackpot_value = 0
    jackpot_won = False
    
    first_prize_value = 0
    first_prize_winners = 0
    second_prize_value = 0
    second_prize_winners = 0
    third_prize_value = 0
    third_prize_winners = 0
    
    for row in soup.select("table.table-hover tbody tr"):
        cols = row.select("td")
        if cols:
            prize_name = cols[0].text.strip()
            winners_str = cols[2].text.strip()
            prize_val_str = cols[3].text.strip()
            val = int(''.join(c for c in prize_val_str if c.isdigit()))
            winners = int(''.join(c for c in winners_str if c.isdigit()))
            
            if "Jackpot" in prize_name:
                jackpot_value = val
                jackpot_won = winners > 0
            elif "Giải Nhất" in prize_name:
                first_prize_value = val
                first_prize_winners = winners
            elif "Giải Nhì" in prize_name:
                second_prize_value = val
                second_prize_winners = winners
            elif "Giải Ba" in prize_name:
                third_prize_value = val
                third_prize_winners = winners

    print("Jackpot:", jackpot_value, "Won:", jackpot_won)
    print("First Prize:", first_prize_value, "Winners:", first_prize_winners)
    print("Second Prize:", second_prize_value, "Winners:", second_prize_winners)
    print("Third Prize:", third_prize_value, "Winners:", third_prize_winners)
