import asyncio
import logging
from app.services.ai_service import generate_prediction
from app.core.database import async_session
from app.models.draw_result import DrawResult
from sqlalchemy import select, desc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_next_period(lottery_type: str):
    async with async_session() as db:
        result = await db.execute(
            select(DrawResult)
            .where(DrawResult.type == lottery_type)
            .order_by(desc(DrawResult.draw_period))
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        if not latest:
            return "00001"
        
        period_int = int(latest.draw_period)
        return f"{period_int + 1:05d}"

async def main():
    for ltype in ["mega645", "power655"]:
        next_p = await get_next_period(ltype)
        logger.info(f"Generating prediction for {ltype} period {next_p}...")
        await generate_prediction(next_p, ltype)

if __name__ == "__main__":
    asyncio.run(main())
