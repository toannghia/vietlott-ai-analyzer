import asyncio
from app.core.database import async_session
from app.models.draw_result import DrawResult
from sqlalchemy import select, update

async def migrate():
    async with async_session() as db:
        r = await db.execute(select(DrawResult))
        results = r.scalars().all()
        
        count = 0
        for res in results:
            if len(res.draw_period) < 5 and res.draw_period.isdigit():
                new_period = res.draw_period.zfill(5)
                await db.execute(
                    update(DrawResult)
                    .where(DrawResult.id == res.id)
                    .values(draw_period=new_period)
                )
                count += 1
        
        await db.commit()
        print(f"Migrated {count} draw_period values.")

if __name__ == "__main__":
    asyncio.run(migrate())
