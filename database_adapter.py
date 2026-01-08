# database_adapter.py
"""
Database Adapter - Provides a unified interface for multiple database types.
Supports SQLite and PostgreSQL with extensible architecture.
"""

import sqlite3
from typing import Optional, List, Tuple, Any, Dict
from abc import ABC, abstractmethod
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql as pg_sql
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close database connection."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        """Execute a query and return (columns, rows)."""
        pass
    
    @abstractmethod
    def get_schema(self) -> str:
        """Get human-readable schema description."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the connection is valid."""
        pass


class SQLiteAdapter(DatabaseAdapter):
    """Adapter for SQLite databases."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"[SQLite] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close SQLite connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        """Execute query on SQLite."""
        if not self.connection:
            self.connect()
        
        cur = self.connection.cursor()
        cur.execute(query)
        
        if query.strip().upper().startswith("SELECT"):
            rows = cur.fetchall()
            columns = [col[0] for col in cur.description] if cur.description else []
            return columns, [tuple(r) for r in rows]
        else:
            self.connection.commit()
            return [], []
    
    def get_schema(self) -> str:
        """Get SQLite schema."""
        if not self.connection:
            self.connect()
        
        cur = self.connection.cursor()
        
        # Get all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cur.fetchall()]
        
        schema_lines = ["Tables and Columns:", ""]
        
        for i, table in enumerate(tables, 1):
            schema_lines.append(f"{i}) {table}")
            
            # Get column info
            cur.execute(f"PRAGMA table_info({table});")
            columns = cur.fetchall()
            
            for col in columns:
                col_id, name, col_type, not_null, default_val, is_pk = col
                col_desc = f"   - {name} ({col_type}"
                if is_pk:
                    col_desc += ", PK"
                col_desc += ")"
                schema_lines.append(col_desc)
            
            schema_lines.append("")
        
        return "\n".join(schema_lines)
    
    def test_connection(self) -> bool:
        """Test SQLite connection."""
        try:
            if not self.connection:
                self.connect()
            cur = self.connection.cursor()
            cur.execute("SELECT 1;")
            return True
        except:
            return False


class PostgreSQLAdapter(DatabaseAdapter):
    """Adapter for PostgreSQL databases."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: str = ""
    ):
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 is required for PostgreSQL. Install with: pip install psycopg2-binary")
        
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return True
        except Exception as e:
            print(f"[PostgreSQL] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close PostgreSQL connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        """Execute query on PostgreSQL."""
        if not self.connection:
            self.connect()
        
        cur = self.connection.cursor()
        cur.execute(query)
        
        if query.strip().upper().startswith("SELECT"):
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description] if cur.description else []
            return columns, rows
        else:
            self.connection.commit()
            return [], []
    
    def get_schema(self) -> str:
        """Get PostgreSQL schema."""
        if not self.connection:
            self.connect()
        
        cur = self.connection.cursor()
        
        # Get all tables in public schema
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        schema_lines = ["Tables and Columns:", ""]
        
        for i, table in enumerate(tables, 1):
            schema_lines.append(f"{i}) {table}")
            
            # Get column info
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table,))
            columns = cur.fetchall()
            
            for col in columns:
                name, col_type, nullable, default = col
                col_desc = f"   - {name} ({col_type}"
                if nullable == 'NO':
                    col_desc += ", NOT NULL"
                col_desc += ")"
                schema_lines.append(col_desc)
            
            # Get primary key
            cur.execute("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY';
            """, (table,))
            pk_cols = [row[0] for row in cur.fetchall()]
            
            if pk_cols:
                schema_lines.append(f"   - Primary Keys: {', '.join(pk_cols)}")
            
            schema_lines.append("")
        
        return "\n".join(schema_lines)
    
    def test_connection(self) -> bool:
        """Test PostgreSQL connection."""
        try:
            if not self.connection:
                self.connect()
            cur = self.connection.cursor()
            cur.execute("SELECT 1;")
            return True
        except:
            return False


class DatabaseFactory:
    """Factory for creating database adapters."""
    
    @staticmethod
    def create_adapter(
        db_type: str,
        **kwargs
    ) -> DatabaseAdapter:
        """
        Create appropriate database adapter.
        
        Args:
            db_type: "sqlite" or "postgresql"
            **kwargs: Connection parameters
            
        Returns:
            DatabaseAdapter instance
        """
        db_type = db_type.lower()
        
        if db_type == "sqlite":
            return SQLiteAdapter(kwargs.get("db_path", "test_db.sqlite"))
        
        elif db_type in ["postgresql", "postgres"]:
            return PostgreSQLAdapter(
                host=kwargs.get("host", "localhost"),
                port=kwargs.get("port", 5432),
                database=kwargs.get("database", "postgres"),
                user=kwargs.get("user", "postgres"),
                password=kwargs.get("password", "")
            )
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")


# Current adapter singleton
_current_adapter: Optional[DatabaseAdapter] = None


def get_current_adapter() -> Optional[DatabaseAdapter]:
    """Get the currently active database adapter."""
    return _current_adapter


def set_current_adapter(adapter: DatabaseAdapter):
    """Set the active database adapter."""
    global _current_adapter
    _current_adapter = adapter


def create_and_set_adapter(db_type: str, **kwargs) -> DatabaseAdapter:
    """Create adapter and set as current."""
    adapter = DatabaseFactory.create_adapter(db_type, **kwargs)
    if adapter.connect():
        set_current_adapter(adapter)
    return adapter
