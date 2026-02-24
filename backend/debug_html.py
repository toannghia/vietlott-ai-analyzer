import asyncio
from app.services.crawler import fetch_vietlott_html

async def run():
    print("Fetching HTML...")
    html = await fetch_vietlott_html("https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/mega-6-45")
    with open("vietlott.html", "w") as f:
        f.write(html)
    print("Saved to vietlott.html")

if __name__ == "__main__":
    asyncio.run(run())
