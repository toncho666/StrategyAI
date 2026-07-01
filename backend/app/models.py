from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class SignalResponse(BaseModel):
    """Модель сигнала для ответа API"""
    strategyName: str = Field(..., description="Название стратегии")
    asset: str = Field(..., description="Торговый актив")
    type: str = Field(..., description="Тип сигнала (buy/sell)")
    positionVolume: float = Field(..., description="Объем позиции")
    openingPrice: float = Field(..., description="Цена открытия")
    stopLoss: float = Field(..., description="Стоп-лосс")
    takeProfit: float = Field(..., description="Тейк-профит")
    timestamp: datetime = Field(..., description="Время создания сигнала")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StrategyInfo(BaseModel):
    """Информация о стратегии"""
    name: str = Field(..., description="Название стратегии")
    timeframe: str = Field(..., description="Таймфрейм")
    asset: str = Field(..., description="Актив")
    createdAt: date = Field(..., alias="createdat", description="Дата создания")  # Добавлен alias
    
    class Config:
        populate_by_name = True  # Разрешить заполнение по имени или по alias
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class DailyStats(BaseModel):
    """Дневная статистика стратегии"""
    dt: date = Field(..., description="Дата")
    profit_on_date: float = Field(..., description="Прибыль за день")
    profit_to_date: float = Field(..., description="Прибыль накопленная")
    profitability_on_date: float = Field(..., description="Доходность за день")
    profitability_to_date: float = Field(..., description="Доходность накопленная")
    annual_252_profitability_to_date: float = Field(..., description="Годовая доходность (252 дня)")
    annual_365_profitability_to_date: float = Field(..., description="Годовая доходность (365 дней)")
    trades_on_date: int = Field(..., description="Количество сделок за день")
    trades_to_date: int = Field(..., description="Количество сделок накопленное")
    dynamic_win_rate: float = Field(..., description="Винрейт")
    avg_profitable_trade_on_date: float = Field(..., description="Средняя прибыльная сделка за день")
    avg_profitable_trade_to_date: float = Field(..., description="Средняя прибыльная сделка накопленная")
    avg_losing_trade_on_date: float = Field(..., description="Средняя убыточная сделка за день")
    avg_losing_trade_to_date: float = Field(..., description="Средняя убыточная сделка накопленная")
    max_drawdown_on_date: float = Field(..., description="Максимальная просадка за день")
    max_drawdown_to_date: float = Field(..., description="Максимальная просадка накопленная")


class StrategyStatsResponse(BaseModel):
    """Ответ со статистикой стратегий"""
    strategies: dict[str, dict] = Field(..., description="Словарь со статистикой по стратегиям")