import asyncio
import logging
from app.services.ai_service import generate_prediction, verify_prediction
from app.core.database import async_session
from app.models.draw_result import DrawResult
from sqlalchemy import select, desc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_accuracy_history(lottery_type: str = "mega645", count: int = 30):
    async with async_session() as db:
        # Get recent draws to "predict" for
        result = await db.execute(
            select(DrawResult)
            .where(DrawResult.type == lottery_type)
            .order_by(desc(DrawResult.draw_period))
            .limit(count + 1)
        )
        draws = result.scalars().all()
        
        if not draws:
            logger.warning(f"No draws found for {lottery_type}")
            return

        # We need to process from oldest to newest to simulate a sequence
        draws = list(reversed(draws))
        
        
        for i in range(1, len(draws)):
            current_draw = draws[i]
            # Predict for current_draw based on previous data
            logger.info(f"Seeding prediction for {lottery_type} period {current_draw.draw_period}...")
            await generate_prediction(current_draw.draw_period, lottery_type)
            
            # Verify immediately
            logger.info(f"Verifying prediction for {lottery_type} period {current_draw.draw_period}...")
            await verify_prediction(current_draw.draw_period, current_draw.numbers, lottery_type)

        # GENERATE THE ACTUAL FUTURE PREDICTION
        last_draw = draws[-1]
        try:
            next_period_int = int(last_draw.draw_period) + 1
            next_period = f"{next_period_int:05d}"
            logger.info(f"Generating future prediction for {lottery_type} period {next_period}...")
            await generate_prediction(next_period, lottery_type)
        except Exception as e:
            logger.error(f"Failed to generate future prediction: {e}")

async def main():
    await seed_accuracy_history("mega645", 30)
    await seed_accuracy_history("power655", 30)

if __name__ == "__main__":
    asyncio.run(main())
