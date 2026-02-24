import subprocess
from bs4 import BeautifulSoup
import asyncio

async def fetch(url):
    cmd = [
        "curl", "--http1.1", "-v", "-s", "-L",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        url
    ]
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: subprocess.run(cmd, capture_output=True, text=True, errors="replace"))
    if result.stderr:
        print(f"--- CURL VERBOSE START ---\n{result.stderr}\n--- CURL VERBOSE END ---")
    return result.stdout

async def main():
    url = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-655?p=2"
    print(f"Testing URL: {url}")
    html = await fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table.table-hover tbody tr")
    print(f"Found {len(rows)} rows")
    for i, row in enumerate(rows[:3]):
        period = row.select("td")[1].get_text(strip=True)
        print(f"Row {i+1} period: {period}")

if __name__ == '__main__':
    asyncio.run(main())
