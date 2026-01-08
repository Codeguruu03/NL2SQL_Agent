# tests/test_db.py
"""
Tests for the database module.
"""
import pytest
import sqlite3
from pathlib import Path
import tempfile
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import (
    init_db,
    get_connection,
    run_query,
    get_schema_text,
    auto_detect_schema,
    set_database_path,
    reset_to_default_database,
    DB_PATH
)


class TestDatabaseConnection:
    """Tests for database connection functionality."""
    
    def test_init_db_creates_tables(self):
        """Test that init_db creates all required tables."""
        # Initialize the database
        init_db()
        
        # Check tables exist
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cur.fetchall()]
        
        assert "department" in tables
        assert "usermaster" in tables
        assert "UserSkillAndRatings" in tables
        
        conn.close()
    
    def test_run_query_select(self):
        """Test running a SELECT query."""
        init_db()
        
        columns, rows = run_query("SELECT * FROM department;")
        
        assert columns is not None
        assert len(columns) == 2
        assert "dept_id" in columns or "dept_name" in columns
        assert len(rows) >= 0
    
    def test_run_query_with_join(self):
        """Test running a JOIN query."""
        init_db()
        
        sql = """
        SELECT u.full_name, d.dept_name 
        FROM usermaster u 
        LEFT JOIN department d ON u.dept_id = d.dept_id;
        """
        
        columns, rows = run_query(sql)
        
        assert columns is not None
        assert "full_name" in columns
        assert "dept_name" in columns
    
    def test_run_query_invalid_sql(self):
        """Test that invalid SQL raises an exception."""
        init_db()
        
        with pytest.raises(Exception):
            run_query("SELECT * FROM nonexistent_table;")


class TestSchemaDetection:
    """Tests for schema auto-detection."""
    
    def test_get_schema_text(self):
        """Test getting schema text."""
        schema = get_schema_text()
        
        assert schema is not None
        assert "department" in schema
        assert "usermaster" in schema
        assert "UserSkillAndRatings" in schema
    
    def test_auto_detect_schema(self):
        """Test auto schema detection."""
        init_db()
        
        schema = auto_detect_schema()
        
        assert "department" in schema
        assert "usermaster" in schema
        assert "dept_id" in schema
        assert "full_name" in schema
    
    def test_auto_detect_schema_custom_db(self):
        """Test auto schema detection with custom database."""
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
            temp_path = f.name
        
        try:
            # Create a simple database
            conn = sqlite3.connect(temp_path)
            cur = conn.cursor()
            cur.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);")
            cur.execute("INSERT INTO test_table VALUES (1, 'test');")
            conn.commit()
            conn.close()
            
            # Detect schema
            schema = auto_detect_schema(Path(temp_path))
            
            assert "test_table" in schema
            assert "id" in schema
            assert "name" in schema
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestDatabasePath:
    """Tests for database path management."""
    
    def test_set_database_path_valid(self):
        """Test setting a valid database path."""
        init_db()  # Ensure default DB exists
        
        result = set_database_path(str(DB_PATH))
        
        assert result == True
    
    def test_set_database_path_invalid(self):
        """Test setting an invalid database path."""
        result = set_database_path("/nonexistent/path/database.sqlite")
        
        assert result == False
    
    def test_reset_to_default(self):
        """Test resetting to default database."""
        reset_to_default_database()
        # Should not raise any exceptions


# Run tests with: pytest tests/test_db.py -v
