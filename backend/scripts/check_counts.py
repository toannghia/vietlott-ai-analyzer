import asyncio
from app.core.database import async_session
from app.models.draw_result import DrawResult
from sqlalchemy import select, func

async def check():
    async with async_session() as db:
        for l_type in ["mega645", "power655"]:
            r = await db.execute(select(func.count()).where(DrawResult.type == l_type))
            count = r.scalar()
            
            # Fetch latest one
            latest_r = await db.execute(
                select(DrawResult).where(DrawResult.type == l_type).order_by(DrawResult.draw_period.desc()).limit(1)
            )
            latest = latest_r.scalar()
            latest_period = latest.draw_period if latest else "N/A"
            
            print(f"{l_type} count: {count}, Latest Period: {latest_period}")

if __name__ == "__main__":
    asyncio.run(check())
