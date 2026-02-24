from typing import Any, List

from fastapi import APIRouter
from app.services.statistics import get_frequency_stats, get_gap_stats, get_summary_stats, get_cooccurrence_stats

router = APIRouter()

@router.get("/summary")
async def read_stats_summary(type: str = "mega645") -> Any:
    """
    Retrieve Top 6 most and least frequent numbers.
    Useful for dashboard display blocks.
    """
    stats = await get_summary_stats(lottery_type=type)
    return stats

@router.get("/cooccurrence")
async def read_cooccurrence_stats(type: str = "mega645") -> Any:
    """
    Retrieve Top pairs and triplets that appear together frequently.
    """
    stats = await get_cooccurrence_stats(lottery_type=type)
    return stats

@router.get("/frequency")
async def read_number_frequencies(type: str = "mega645") -> Any:
    """
    Retrieve frequency for all numbers.
    Includes Hot/Cold classification based on recent draws.
    """
    stats = await get_frequency_stats(lottery_type=type)
    return {"data": stats}

@router.get("/gaps")
async def read_number_gaps(type: str = "mega645") -> Any:
    """
    Retrieve gap statistics for all numbers.
    Sorted by current_gap descending to easily spot "overdue" numbers.
    """
    stats = await get_gap_stats(lottery_type=type)
    return {"data": stats}
