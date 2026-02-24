from datetime import date

from sqlalchemy import Integer, Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class NumberStat(Base):
    __tablename__ = "number_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True, default="mega645", comment="Loại vé: mega645, power655")
    frequency: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_seen: Mapped[date | None] = mapped_column(Date, nullable=True)
    max_gap: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_gap: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('number', 'type', name='uix_number_type'),
    )

    def __repr__(self) -> str:
        return f"<NumberStat number={self.number} freq={self.frequency} gap={self.current_gap}>"
