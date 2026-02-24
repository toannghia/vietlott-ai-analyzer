import asyncio

def mock_parse(html):
    return {
        "draw_period": "01234",
        "draw_date": "2026-02-22",
        "numbers": [12, 15, 20, 25, 30, 45],
        "jackpot_value": 15000000000,
        "jackpot_won": False
    }

async def run_mock_crawler():
    from app.core.database import async_session
    from app.models.draw_result import DrawResult
    from sqlalchemy import select
    from datetime import datetime

    print("Running mock crawler...")
    data = mock_parse("mock")
    async with async_session() as db:
        new_draw = DrawResult(
            draw_date=datetime.strptime(data["draw_date"], "%Y-%m-%d").date(),
            draw_period=data["draw_period"],
            numbers=data["numbers"],
            type="mega645",
            jackpot_won=data["jackpot_won"],
            jackpot_value=data["jackpot_value"],
            raw_html_log="<mock>html</mock>"
        )
        db.add(new_draw)
        await db.commit()
        print("Mock execution inserted DrawResult.")
        
        verify = await db.execute(select(DrawResult).where(DrawResult.draw_period == "01234"))
        row = verify.scalar_one_or_none()
        print("DB Verification:", row)

if __name__ == "__main__":
    asyncio.run(run_mock_crawler())
