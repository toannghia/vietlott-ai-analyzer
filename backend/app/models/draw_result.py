from datetime import date, datetime

from sqlalchemy import Date, String, Text, BigInteger, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DrawResult(Base):
    __tablename__ = "draw_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    draw_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    draw_period: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    numbers: Mapped[list[int]] = mapped_column(ARRAY(INTEGER), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True, comment="Loại vé: mega645, power655, max3d...")
    
    __table_args__ = (
        UniqueConstraint('draw_period', 'type', name='uix_draw_period_type'),
    )
    
    jackpot_won: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="Kỳ này có người trúng Jackpot không")
    jackpot_value: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="Giá trị Jackpot 1 (VND)")
    jackpot_winners: Mapped[int] = mapped_column(INTEGER, default=0, nullable=False)
    
    jackpot2_value: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="Giá trị Jackpot 2 (VND)")
    jackpot2_winners: Mapped[int] = mapped_column(INTEGER, default=0, nullable=False)
    
    first_prize_value: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    first_prize_winners: Mapped[int] = mapped_column(INTEGER, default=0, nullable=False)
    
    second_prize_value: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    second_prize_winners: Mapped[int] = mapped_column(INTEGER, default=0, nullable=False)
    
    third_prize_value: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    third_prize_winners: Mapped[int] = mapped_column(INTEGER, default=0, nullable=False)
    
    raw_html_log: Mapped[str | None] = mapped_column(Text, nullable=True, comment="HTML thô dự phòng")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<DrawResult period={self.draw_period} date={self.draw_date} type={self.type}>"
