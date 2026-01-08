# src/core/__init__.py
"""
Core modules - Database and API client infrastructure.
"""

from .db import (
    init_db,
    get_connection,
    run_query,
    get_schema_text,
    auto_detect_schema,
    set_database_path,
    get_current_database_path,
    reset_to_default_database
)
from .openrouter_client import OpenRouterClient, get_openrouter_client
from .database_adapter import (
    DatabaseAdapter,
    SQLiteAdapter,
    PostgreSQLAdapter,
    DatabaseFactory,
    get_current_adapter,
    set_current_adapter,
    create_and_set_adapter
)

__all__ = [
    # Database
    "init_db", "get_connection", "run_query", "get_schema_text",
    "auto_detect_schema", "set_database_path", "get_current_database_path",
    "reset_to_default_database",
    
    # API Client
    "OpenRouterClient", "get_openrouter_client",
    
    # Database Adapter
    "DatabaseAdapter", "SQLiteAdapter", "PostgreSQLAdapter",
    "DatabaseFactory", "get_current_adapter", "set_current_adapter",
    "create_and_set_adapter"
]
