import asyncio
from app.core.database import async_session
from sqlalchemy import text

async def fix():
    async with async_session() as db:
        # Check constraints
        res = await db.execute(text("""
            SELECT conname 
            FROM pg_constraint 
            WHERE conrelid = 'draw_results'::regclass AND contype = 'u';
        """))
        for row in res:
            print(f"Found unique constraint: {row[0]}")
            await db.execute(text(f'ALTER TABLE draw_results DROP CONSTRAINT IF EXISTS "{row[0]}" CASCADE'))
            
        # Also check indexes (draw_period: Mapped[str] = mapped_column(..., unique=True) often creates a unique index)
        # In SQLAlchemy + Postgres, unique=True creates a UNIQUE INDEX or CONSTRAINT named after the column/table
        await db.execute(text("DROP INDEX IF EXISTS ix_draw_results_draw_period"))
        
        # Now add the composite unique constraint
        await db.execute(text("""
            ALTER TABLE draw_results 
            ADD CONSTRAINT uix_draw_period_type UNIQUE (draw_period, type)
        """))
        
        await db.commit()
        print("Successfully updated constraints.")

if __name__ == "__main__":
    asyncio.run(fix())
