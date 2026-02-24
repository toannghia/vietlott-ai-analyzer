import asyncio
from app.core.database import async_session
from app.models.draw_result import DrawResult
from sqlalchemy import text, select, delete

async def cleanup_and_fix():
    print("Starting DB cleanup and constraint fix...")
    async with async_session() as db:
        # 1. DROP old constraint/index if it exists
        print("Dropping old constraints/indexes...")
        await db.execute(text("ALTER TABLE draw_results DROP CONSTRAINT IF EXISTS draw_results_draw_period_key CASCADE"))
        await db.execute(text("DROP INDEX IF EXISTS ix_draw_results_draw_period"))
        await db.commit()
        
        # 2. Identify duplicates (based on integer value of period + type)
        print("Identifying duplicate periods...")
        r = await db.execute(select(DrawResult))
        all_res = r.scalars().all()
        
        # Group by (int(period), type)
        grouped = {}
        for res in all_res:
            try:
                p_int = int(res.draw_period)
                key = (p_int, res.type)
                if key not in grouped:
                    grouped[key] = []
                grouped[key].append(res)
            except ValueError:
                continue
        
        to_delete = []
        to_update = []
        
        for key, res_list in grouped.items():
            # Standardize everything to 5-digit padded
            padded_period = f"{key[0]:05d}"
            
            # If we have multiple, pick one to keep
            res_list.sort(key=lambda x: (len(x.draw_period), x.created_at), reverse=True)
            keep = res_list[0]
            
            # Mark others for deletion
            for other in res_list[1:]:
                to_delete.append(other.id)
                
            # If keep has wrong format, mark for update
            if keep.draw_period != padded_period:
                to_update.append((keep.id, padded_period))
        
        print(f"Cleanup: Found {len(to_delete)} duplicates to delete and {len(to_update)} to pad.")
        
        if to_delete:
            # Batch delete
            for i in range(0, len(to_delete), 100):
                batch = to_delete[i:i+100]
                await db.execute(delete(DrawResult).where(DrawResult.id.in_(batch)))
        
        if to_update:
            # Update periods to padded version
            for rid, p_str in to_update:
                await db.execute(text("UPDATE draw_results SET draw_period = :p WHERE id = :id"), {"p": p_str, "id": rid})
        
        await db.commit()
        
        # 3. Add new composite constraint
        print("Adding composite unique constraint...")
        await db.execute(text("""
            ALTER TABLE draw_results 
            ADD CONSTRAINT uix_draw_period_type UNIQUE (draw_period, type)
        """))
        await db.commit()
        print("Successfully cleaned up and fixed DB constraints.")

if __name__ == "__main__":
    asyncio.run(cleanup_and_fix())
