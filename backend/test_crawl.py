import asyncio
import httpx
from bs4 import BeautifulSoup

async def main():
    url = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/mega-6-45"
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(url)
        print("Status:", resp.status_code)
        soup = BeautifulSoup(resp.text, 'html.parser')
        print(soup.select_one('.chitiet-ketqua-title').text.strip())

asyncio.run(main())
