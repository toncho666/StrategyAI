from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.models import SignalResponse
from app.database import execute_query
from app.logger import logger

router = APIRouter(tags=["signals"])

@router.get("/", response_model=List[SignalResponse])
async def get_signals(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Количество сигналов для получения"
    )
):
    """
    Получение последних сигналов
    
    Возвращает список сигналов с сортировкой по времени создания (сначала новые)
    """
    query = """
        SELECT
            REPLACE(strategy_name, '.py', '') AS "strategyName",
            CONCAT(symbol, '(', timeframe, ')') AS asset,
            close_price AS "openingPrice",
            stop_loss AS "stopLoss",
            take_profit AS "takeProfit",
            volume AS "positionVolume",
            side AS type,
            created_at AS "timestamp"
        FROM test.signals
        ORDER BY created_at DESC
        LIMIT %s
    """
    
    try:
        results = execute_query(query, (limit,))
        return results
    except Exception as e:
        logger.error(f"Error fetching signals: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database query error: {str(e)}"
        )


@router.get("/latest", response_model=List[SignalResponse])
async def get_latest_signals(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Количество последних сигналов"
    )
):
    """
    Получение последних N сигналов
    
    Упрощенный метод для быстрого доступа к последним сигналам
    """
    return await get_signals(limit)