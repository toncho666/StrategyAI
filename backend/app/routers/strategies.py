from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional

from app.models import StrategyInfo, StrategyStatsResponse
from app.database import execute_query, get_db_cursor
from app.logger import logger

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.get("/list", response_model=List[StrategyInfo])
async def get_strategies_list():
    """
    Получение списка активных стратегий
    
    Возвращает список стратегий с информацией о них
    """
    query = """
        SELECT 
            name,
            timeframe,
            asset,
            createdat::date AS createdat
        FROM test.strategy_info
        WHERE expirationdate > NOW()
        ORDER BY id
    """
    
    try:
        results = execute_query(query)
        
        if not results:
            return []
        
        return results
    except Exception as e:
        logger.error(f"Error fetching strategies list: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database query error: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_all_strategies_stats():
    """
    Получение статистики по всем активным стратегиям
    
    Возвращает полную статистику по каждой стратегии:
    - Ежедневная статистика (hist)
    - Последний день статистики (last)
    """
    try:
        # Получаем список активных стратегий
        strategies = execute_query("""
            SELECT 
                name,
                createdat::date
            FROM test.strategy_info
            WHERE expirationdate > NOW()
            ORDER BY id
        """)
        
        if not strategies:
            raise HTTPException(
                status_code=404,
                detail="No active strategies found"
            )
        
        result = {"strategies": {}}
        
        for strategy in strategies:
            strategy_name = strategy['name']
            table_name = f"test.{strategy_name}_daily_stat"
            

            query = f"""
                WITH constants AS (
                    SELECT EXTRACT(DAY FROM max("timestamp") - min("timestamp")) AS days_diff
                    FROM test.btc_usd_t
                )
                SELECT 
                    "date" AS dt,
                    SUM(total_profit_today) AS profit_on_date,
                    ROUND(SUM(SUM(total_profit_today)) OVER (ORDER BY "date")::NUMERIC, 2) AS profit_to_date,
                    SUM(profitability_dynamic) AS profitability_on_date,
                    ROUND(SUM(SUM(profitability_dynamic)) OVER (ORDER BY "date")::NUMERIC, 2) AS profitability_to_date,
                    ROUND((SUM(SUM(profitability_dynamic)) OVER (ORDER BY "date") / c.days_diff)::NUMERIC * 252, 2) AS annual_252_profitability_to_date,
                    ROUND((SUM(SUM(profitability_dynamic)) OVER (ORDER BY "date") / c.days_diff)::NUMERIC * 365, 2) AS annual_365_profitability_to_date,
                    SUM(trade_count) AS trades_on_date,
                    SUM(SUM(trade_count)) OVER (ORDER BY "date") AS trades_to_date,
                    ROUND(SUM(SUM((win_rate/100) * trade_count)) OVER (ORDER BY "date")::NUMERIC /
                        NULLIF(SUM(SUM(trade_count)) OVER (ORDER BY "date")::NUMERIC, 0), 2)*100 AS dynamic_win_rate,
                    SUM(avg_profitable_trade) AS avg_profitable_trade_on_date,
                    SUM(SUM(avg_profitable_trade)) OVER (ORDER BY "date") AS avg_profitable_trade_to_date,
                    SUM(avg_losing_trade) AS avg_losing_trade_on_date,
                    ROUND(SUM(SUM(avg_losing_trade)) OVER (ORDER BY "date")::NUMERIC, 2) AS avg_losing_trade_to_date,
                    MIN(max_drawdown) AS max_drawdown_on_date,
                    MIN(MIN(max_drawdown)) OVER (ORDER BY "date") AS max_drawdown_to_date
                FROM {table_name}, constants c
                GROUP BY "date", c.days_diff
                ORDER BY "date" ASC
            """
            
            # Используем прямой доступ к курсору для конвертации типов
            with get_db_cursor() as cursor:
                cursor.execute(query)
                hist_results = cursor.fetchall()
                
                # Конвертируем Decimal в float
                for row in hist_results:
                    for key, value in list(row.items()):
                        if hasattr(value, 'to_eng_string'):
                            row[key] = float(value)
            
            result["strategies"][strategy_name] = {
                "hist": hist_results,
                "last": hist_results[-1] if hist_results else None
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching strategies stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database query error: {str(e)}"
        )


@router.get("/{strategy_name}/stats", response_model=Dict[str, Any])
async def get_strategy_stats(strategy_name: str):
    """
    Получение статистики по конкретной стратегии
    
    Args:
        strategy_name: Название стратегии
    """
    try:
        # Проверяем существование стратегии
        strategy = execute_query("""
            SELECT name
            FROM test.strategy_info
            WHERE name = %s AND expirationdate > NOW()
        """, (strategy_name,), fetch_one=True)
        
        if not strategy:
            raise HTTPException(
                status_code=404,
                detail=f"Strategy '{strategy_name}' not found or inactive"
            )
        
        # Получаем статистику для конкретной стратегии
        stats = await get_all_strategies_stats()
        
        if strategy_name not in stats["strategies"]:
            raise HTTPException(
                status_code=404,
                detail=f"No statistics found for strategy '{strategy_name}'"
            )
        
        return {
            "strategy": strategy_name,
            "stats": stats["strategies"][strategy_name]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching strategy stats for {strategy_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database query error: {str(e)}"
        )