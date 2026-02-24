import asyncio
from app.core.database import async_session
from app.models.user import User
from app.models.draw_result import DrawResult
from sqlalchemy import select, func

async def main():
    async with async_session() as session:
        user_count = await session.scalar(select(func.count()).select_from(User))
        mega_count = await session.scalar(select(func.count()).select_from(DrawResult).where(DrawResult.type == 'mega645'))
        power_count = await session.scalar(select(func.count()).select_from(DrawResult).where(DrawResult.type == 'power655'))
        
        print(f"Users: {user_count}")
        print(f"Mega: {mega_count}")
        print(f"Power: {power_count}")

if __name__ == "__main__":
    asyncio.run(main())
