from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc, func
from app.core.database import async_session
from app.models.ai_prediction import AIPrediction
from app.api.deps import get_current_user_optional
from app.models.user import User, UserRole

router = APIRouter()

@router.get("/latest")
async def get_latest_prediction(
    type: str = "mega645",
    current_user: User | None = Depends(get_current_user_optional)
):
    async with async_session() as db:
        result = await db.execute(
            select(AIPrediction)
            .where(AIPrediction.type == type)
            .order_by(desc(AIPrediction.target_period))
            .limit(1)
        )
        prediction = result.scalar_one_or_none()
        
        if not prediction:
            raise HTTPException(status_code=404, detail=f"No predictions available for {type} yet")
            
        is_premium_user = current_user and current_user.role in [UserRole.PREMIUM, UserRole.ADMIN]
        
        if prediction.is_premium_only and not is_premium_user:
            return {
                "target_period": prediction.target_period,
                "type": prediction.type,
                "predicted_numbers": prediction.predicted_numbers[:3] + ["?", "?", "?"],
                "prediction_sets": [],
                "confidence": "Premium Only",
                "message": "Upgrade to Premium to unlock the full AI predicted sequence and confidence rating."
            }
            
        return {
            "target_period": prediction.target_period,
            "type": prediction.type,
            "predicted_numbers": prediction.predicted_numbers,
            "prediction_sets": prediction.prediction_sets or [],
            "confidence": prediction.confidence,
            "is_verified": prediction.is_verified,
            "matches": prediction.matches,
            "message": "AI sequence unlocked. Good luck!"
        }


@router.get("/accuracy")
async def get_prediction_accuracy(type: str = "mega645"):
    """Return accuracy stats for all verified predictions."""
    from app.models.draw_result import DrawResult
    
    async with async_session() as db:
        # Get all verified predictions with their actual draw results
        result = await db.execute(
            select(AIPrediction, DrawResult.numbers)
            .outerjoin(
                DrawResult, 
                (AIPrediction.target_period == DrawResult.draw_period) & (AIPrediction.type == DrawResult.type)
            )
            .where((AIPrediction.is_verified == True) & (AIPrediction.type == type))
            .order_by(desc(AIPrediction.target_period))
            .limit(50)
        )
        verified_data = result.all()
        
        # Get total predictions
        total_result = await db.execute(
            select(func.count(AIPrediction.id))
            .where(AIPrediction.type == type)
        )
        total = total_result.scalar() or 0
        
        # Calculate total verified count
        verified_count_result = await db.execute(
            select(func.count(AIPrediction.id))
            .where((AIPrediction.is_verified == True) & (AIPrediction.type == type))
        )
        verified_count = verified_count_result.scalar() or 0
        
        if verified_count == 0:
            return {
                "total_predictions": total,
                "verified_count": 0,
                "avg_matches": 0,
                "history": []
            }
        
        avg_matches = sum((p.AIPrediction.matches or 0) for p in verified_data) / len(verified_data) if verified_data else 0
        
        return {
            "total_predictions": total,
            "verified_count": verified_count,
            "avg_matches": round(avg_matches, 2),
            "history": [
                {
                    "period": p.AIPrediction.target_period,
                    "predicted": p.AIPrediction.predicted_numbers,
                    "prediction_sets": p.AIPrediction.prediction_sets or [],
                    "matches": p.AIPrediction.matches,
                    "confidence": p.AIPrediction.confidence,
                    "actual": p.numbers
                }
                for p in verified_data
            ]
        }
