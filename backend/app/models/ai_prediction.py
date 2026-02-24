from datetime import datetime

from sqlalchemy import String, Float, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY, INTEGER, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    target_period: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True, default="mega645", comment="Loại vé: mega645, power655")
    
    # Dữ liệu dự báo chính (Top 1) để tương thích ngược với API hiện tại
    predicted_numbers: Mapped[list[int]] = mapped_column(ARRAY(INTEGER), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Dữ liệu 3 bộ dự báo (JSONB)
    prediction_sets: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True, comment="Danh sách Top 3 bộ số dự đoán [{numbers: [], confidence: 85}, ...]")
    
    is_premium_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="Chỉ user Premium mới xem được")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    matches: Mapped[int | None] = mapped_column(INTEGER, nullable=True) # Top 1 matches
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<AIPrediction period={self.target_period} confidence={self.confidence:.2f}>"
