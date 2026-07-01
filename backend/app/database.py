import logging
from contextlib import contextmanager
from typing import Generator

from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError

from app.config import settings

logger = logging.getLogger(__name__)


class DatabasePool:
    """Пул соединений с базой данных"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self):
        """Инициализация пула соединений"""
        if self._pool is None:
            try:
                self._pool = SimpleConnectionPool(
                    minconn=settings.DB_POOL_MIN,
                    maxconn=settings.DB_POOL_MAX,
                    **settings.db_config
                )
                logger.info("Database pool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize database pool: {e}")
                raise RuntimeError(f"Database connection error: {e}")
    
    def get_connection(self):
        """Получить соединение из пула"""
        if self._pool is None:
            self.initialize()
        return self._pool.getconn()
    
    def put_connection(self, conn):
        """Вернуть соединение в пул"""
        if self._pool is not None:
            self._pool.putconn(conn)
    
    def close_all(self):
        """Закрыть все соединения"""
        if self._pool is not None:
            self._pool.closeall()
            logger.info("All database connections closed")


# Синглтон для пула соединений
db_pool = DatabasePool()


@contextmanager
def get_db_connection() -> Generator:
    """
    Контекстный менеджер для работы с соединением БД
    
    Пример использования:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM table")
    """
    conn = db_pool.get_connection()
    try:
        yield conn
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        db_pool.put_connection(conn)


@contextmanager
def get_db_cursor(cursor_factory=RealDictCursor):
    """
    Контекстный менеджер для работы с курсором БД
    
    Пример использования:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=cursor_factory) as cursor:
            yield cursor


def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    """
    Утилита для выполнения запросов к БД
    
    Args:
        query: SQL запрос
        params: Параметры запроса
        fetch_one: Вернуть одну запись или все
    
    Returns:
        Результат запроса
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise