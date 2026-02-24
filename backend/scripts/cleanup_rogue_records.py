import asyncio
from sqlalchemy import delete
from app.core.database import async_session
from app.models.draw_result import DrawResult

async def cleanup_rogue_records():
    async with async_session() as db:
        # Rogue records have negative draw_period (dummy IDs) or empty numbers
        stmt = delete(DrawResult).where(
            (DrawResult.draw_period.like('-%')) | 
            (DrawResult.numbers == [])
        )
        result = await db.execute(stmt)
        await db.commit()
        print(f"Deleted {result.rowcount} rogue records.")

if __name__ == "__main__":
    asyncio.run(cleanup_rogue_records())
