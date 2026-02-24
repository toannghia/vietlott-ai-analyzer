import logging
import itertools
from typing import Dict, List, Any
from collections import defaultdict, Counter

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.draw_result import DrawResult
from app.models.number_stat import NumberStat

logger = logging.getLogger(__name__)

async def update_number_stats(lottery_type: str = "mega645", limit: int = 5000) -> None:
    """
    Recalculate frequency and gap statistics based on the latest DrawResults.
    Upserts records into the NumberStat table.
    """
    try:
        max_num = 55 if lottery_type == "power655" else 45
        async with async_session() as db:
            # Fetch all draw results, ordered by period descending (newest first)
            result = await db.execute(
                select(DrawResult)
                .where(DrawResult.type == lottery_type)
                .order_by(desc(DrawResult.draw_date), desc(DrawResult.draw_period))
                .limit(limit)
            )
            draws = result.scalars().all()

            if not draws:
                logger.info(f"No valid DrawResults found to calculate stats for {lottery_type}.")
                return

            frequencies = defaultdict(int)
            last_seen_dates = {}
            current_gaps = {i: 0 for i in range(1, max_num + 1)}
            max_gaps_tracking = defaultdict(int)
            
            # Note: draws is newest first [Draw100, Draw99, ..., Draw1]
            # To calculate max gaps accurately, we need to iterate chronologically (oldest to newest)
            chronological_draws = list(reversed(draws))
            
            # Temporary tracking for gap calculation
            running_gaps = {i: 0 for i in range(1, max_num + 1)}

            for draw in chronological_draws:
                drawn_nums = set(draw.numbers)
                
                for num in range(1, max_num + 1):
                    if num in drawn_nums:
                        frequencies[num] += 1
                        last_seen_dates[num] = draw.draw_date
                        
                        # Reset running gap for this number
                        if running_gaps[num] > max_gaps_tracking[num]:
                            max_gaps_tracking[num] = running_gaps[num]
                        running_gaps[num] = 0
                    else:
                        running_gaps[num] += 1
            
            # After all draws, the running_gaps represent the current_gap
            for num in range(1, max_num + 1):
                current_gaps[num] = running_gaps[num]
                # Also check if the final running gap is the local maximum
                if running_gaps[num] > max_gaps_tracking[num]:
                    max_gaps_tracking[num] = running_gaps[num]

            # Upsert into NumberStat table
            for num in range(1, max_num + 1):
                stat_result = await db.execute(
                    select(NumberStat)
                    .where((NumberStat.number == num) & (NumberStat.type == lottery_type))
                )
                stat = stat_result.scalar_one_or_none()
                
                if not stat:
                    stat = NumberStat(number=num, type=lottery_type, frequency=0, current_gap=0, max_gap=0)
                    db.add(stat)
                
                stat.frequency = frequencies[num]
                stat.last_seen = last_seen_dates.get(num)
                stat.current_gap = current_gaps[num]
                
                if max_gaps_tracking[num] > stat.max_gap:
                    stat.max_gap = max_gaps_tracking[num]

            await db.commit()
            logger.info(f"Successfully updated Number Stats for {lottery_type}.")
            
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")

async def get_frequency_stats(lottery_type: str = "mega645") -> List[Dict[str, Any]]:
    """Fetch frequency stats and classify Hot/Cold."""
    async with async_session() as db:
        result = await db.execute(
            select(NumberStat)
            .where(NumberStat.type == lottery_type)
            .order_by(desc(NumberStat.frequency), NumberStat.number)
        )
        stats = result.scalars().all()
        
        if not stats:
            return []
            
        return [
            {
                "number": s.number,
                "frequency": s.frequency,
                "classification": "hot" if idx < 5 else ("cold" if idx >= len(stats) - 5 else "neutral")
            }
            for idx, s in enumerate(stats)
        ]

async def get_gap_stats(lottery_type: str = "mega645") -> List[Dict[str, Any]]:
    """Fetch gap stats."""
    async with async_session() as db:
        result = await db.execute(
            select(NumberStat)
            .where(NumberStat.type == lottery_type)
            .order_by(desc(NumberStat.current_gap), NumberStat.number)
        )
        stats = result.scalars().all()
        
        return [
            {
                "number": s.number,
                "current_gap": s.current_gap,
                "max_gap": s.max_gap,
                "last_seen": s.last_seen
            }
            for s in stats
        ]

async def get_summary_stats(lottery_type: str = "mega645") -> Dict[str, Any]:
    """Fetch Top 6 most frequent (Hot) and Top 6 least frequent (Cold) numbers."""
    async with async_session() as db:
        # Most frequent (Hot)
        hot_result = await db.execute(
            select(NumberStat)
            .where(NumberStat.type == lottery_type)
            .order_by(desc(NumberStat.frequency), NumberStat.number)
            .limit(6)
        )
        hot = hot_result.scalars().all()
        
        # Least frequent (Cold)
        cold_result = await db.execute(
            select(NumberStat)
            .where(NumberStat.type == lottery_type)
            .order_by(NumberStat.frequency, NumberStat.number)
            .limit(6)
        )
        cold = cold_result.scalars().all()
        
        return {
            "hot": [{"number": s.number, "frequency": s.frequency} for s in hot],
            "cold": [{"number": s.number, "frequency": s.frequency} for s in cold]
        }

async def get_cooccurrence_stats(lottery_type: str = "mega645", limit: int = 1500) -> Dict[str, Any]:
    """Analyze pairs and triplets frequent co-occurrence."""
    async with async_session() as db:
        result = await db.execute(
            select(DrawResult)
            .where(DrawResult.type == lottery_type)
            .order_by(desc(DrawResult.draw_date))
            .limit(limit)
        )
        draws = result.scalars().all()
        
        pair_counts = Counter()
        triplet_counts = Counter()
        
        for draw in draws:
            nums = sorted(draw.numbers[:6]) # Only main 6 numbers for consistency
            # Pairs
            for pair in itertools.combinations(nums, 2):
                pair_counts[pair] += 1
            # Triplets
            for triplet in itertools.combinations(nums, 3):
                triplet_counts[triplet] += 1
                
        # Get Top 6 of each
        top_pairs = [
            {"numbers": list(p), "count": count} 
            for p, count in pair_counts.most_common(6)
        ]
        top_triplets = [
            {"numbers": list(t), "count": count} 
            for t, count in triplet_counts.most_common(6)
        ]
        
        return {
            "pairs": top_pairs,
            "triplets": top_triplets
        }
