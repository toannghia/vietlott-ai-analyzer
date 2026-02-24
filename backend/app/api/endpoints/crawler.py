from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Any
from sqlalchemy import select, func

from app.api.deps import get_current_admin_user, get_current_user_optional
from app.models.user import User
from app.models.draw_result import DrawResult
from app.core.database import async_session
from app.services.crawler import run_daily_crawler

router = APIRouter()

@router.post("/run")
async def run_crawler_manual(
    background_tasks: BackgroundTasks,
    type: str = "mega645",
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Manually trigger the Vietlott crawling process.
    Requires ADMIN privileges. The task runs in the background.
    """
    background_tasks.add_task(run_daily_crawler, lottery_type=type)
    return {"message": f"Crawler task for {type} dispatched to the background layer. Look at server logs for details."}

@router.get("/history")
async def get_crawler_history(
    type: str = "mega645",
    page: int = 1,
    limit: int = 20,
    current_user: User | None = Depends(get_current_user_optional)
) -> Any:
    """
    Get raw historical draw results with pagination.
    """
    async with async_session() as db:
        # Total count query
        count_stmt = select(func.count()).select_from(DrawResult).where(DrawResult.type == type)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Absolute latest draw query
        latest_stmt = (
            select(DrawResult)
            .where(DrawResult.type == type)
            .order_by(DrawResult.draw_date.desc(), DrawResult.draw_period.desc())
            .limit(1)
        )
        latest_result = await db.execute(latest_stmt)
        latest_draw = latest_result.scalar_one_or_none()

        # Paginated results query
        offset = (page - 1) * limit
        stmt = (
            select(DrawResult)
            .where(DrawResult.type == type)
            .order_by(DrawResult.draw_date.desc(), DrawResult.draw_period.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        draws = result.scalars().all()
        
        return {
            "total": total,
            "latest_draw": {
                "draw_period": latest_draw.draw_period,
                "jackpot_value": latest_draw.jackpot_value,
                "jackpot2_value": latest_draw.jackpot2_value,
            } if latest_draw else None,
            "page": page,
            "limit": limit,
            "data": [
                {
                    "draw_period": d.draw_period,
                    "draw_date": d.draw_date.isoformat(),
                    "numbers": d.numbers,
                    "jackpot_value": d.jackpot_value,
                    "jackpot_winners": d.jackpot_winners,
                    "jackpot2_value": d.jackpot2_value,
                    "jackpot2_winners": d.jackpot2_winners,
                    "first_prize_value": d.first_prize_value,
                    "first_prize_winners": d.first_prize_winners,
                    "second_prize_value": d.second_prize_value,
                    "second_prize_winners": d.second_prize_winners,
                    "third_prize_value": d.third_prize_value,
                    "third_prize_winners": d.third_prize_winners,
                }
                for d in draws
            ]
        }
