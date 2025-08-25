import os
from typing import Optional

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling, errorcode


load_dotenv()


class DatabasePool:
    _pool: Optional[pooling.MySQLConnectionPool] = None

    @classmethod
    def initialize(cls) -> None:
        if cls._pool is None:
            host = os.getenv("DB_HOST", "localhost")
            port = int(os.getenv("DB_PORT", "3306"))
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "IT@admin123456789")
            database = os.getenv("DB_NAME", "krishiAiDb")
            auth_plugin = os.getenv("DB_AUTH_PLUGIN", "mysql_native_password")

            try:
                # Try to create pool directly
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="krishi_pool",
                    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    auth_plugin=auth_plugin,
                )
            except mysql.connector.Error as exc:
                # If database doesn't exist, create it and retry
                if getattr(exc, 'errno', None) == errorcode.ER_BAD_DB_ERROR:
                    admin_conn = mysql.connector.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        auth_plugin=auth_plugin,
                    )
                    try:
                        admin_cursor = admin_conn.cursor()
                        admin_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                        admin_conn.commit()
                    finally:
                        admin_cursor.close()
                        admin_conn.close()
                    # Retry pool creation
                    cls._pool = pooling.MySQLConnectionPool(
                        pool_name="krishi_pool",
                        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                        auth_plugin=auth_plugin,
                    )
                else:
                    raise

    @classmethod
    def get_connection(cls):
        if cls._pool is None:
            cls.initialize()
        return cls._pool.get_connection()


def run_migrations() -> None:
    conn = DatabasePool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()