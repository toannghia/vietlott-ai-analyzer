import httpx
import asyncio
from bs4 import BeautifulSoup

async def fetch():
    url = "https://xskt.com.vn/ket-qua-xo-so-mega-6-45/"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.select("table.result tr")
        for row in rows:
            print(row.text[:100].strip().replace('\n', ' '))

asyncio.run(fetch())
