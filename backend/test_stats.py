import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def run_test():
    from app.services.statistics import update_number_stats, get_frequency_stats, get_gap_stats
    
    # 1. Trigger the background calculation (our DB has the mock draw, so it should process it)
    print("Running stat updates...")
    await update_number_stats()
    
    # 2. Query frequency APIs
    print("\n--- Frequency Stats ---")
    freqs = await get_frequency_stats()
    for f in freqs[:10]: # Print top 10
        print(f)
        
    # 3. Query gaps APIs
    print("\n--- Gap Stats ---")
    gaps = await get_gap_stats()
    for g in gaps[:10]: # Print top 10
        print(g)

if __name__ == "__main__":
    asyncio.run(run_test())
