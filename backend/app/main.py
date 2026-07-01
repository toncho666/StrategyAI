from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import db_pool
from app.routers import signals, strategies
from app.logger import logger

# Создание приложения
app = FastAPI(
    title="Trading Strategies API",
    description="API для управления торговыми стратегиями и получения сигналов",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",  # ← Добавьте /api
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://intellitrade-app-m68ky.ondigitalocean.app",  # Ваш URL
        "http://localhost:5173",  # Для локальной разработки
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(signals.router)
app.include_router(strategies.router)


@app.on_event("startup")
async def startup_event():
    """Инициализация приложения"""
    logger.info("Starting up Trading Strategies API")
    try:
        db_pool.initialize()
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Остановка приложения"""
    logger.info("Shutting down Trading Strategies API")
    db_pool.close_all()
    logger.info("Database connections closed")


@app.get("/health", tags=["health"])
async def health_check():
    """
    Проверка состояния сервиса
    """
    try:
        from app.database import get_db_connection
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


# Для запуска через uvicorn напрямую
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )