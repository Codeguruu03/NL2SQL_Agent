# db.py
import sqlite3
from pathlib import Path
from typing import List, Tuple, Any, Optional, Dict

DB_PATH = Path("test_db.sqlite")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create schema and insert sample data on first run.
    """
    first_time = not DB_PATH.exists()
    conn = get_connection()
    cur = conn.cursor()

    # Create tables
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS department (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS usermaster (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            dept_id INTEGER,
            FOREIGN KEY (dept_id) REFERENCES department(dept_id)
        );

        CREATE TABLE IF NOT EXISTS UserSkillAndRatings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES usermaster(user_id)
        );
        """
    )

    if first_time:
        # Insert sample departments
        cur.executemany(
            "INSERT INTO department (dept_name) VALUES (?)",
            [
                ("Engineering",),
                ("HR",),
                ("Finance",),
            ],
        )

        # Insert sample users
        cur.executemany(
            """
            INSERT INTO usermaster (full_name, email, phone, dept_id)
            VALUES (?, ?, ?, (SELECT dept_id FROM department WHERE dept_name = ?))
            """,
            [
                ("Alice Johnson", "alice@example.com", "9876543210", "Engineering"),
                ("Bob Sharma", "bob@example.com", "9123456780", "HR"),
                ("Charlie Singh", "charlie@example.com", "9988776655", "Engineering"),
                ("Deepa Patel", "deepa@example.com", "9000011111", "Finance"),
            ],
        )

        # Insert sample skills/ratings
        cur.executemany(
            """
            INSERT INTO UserSkillAndRatings (user_id, skill_name, rating)
            VALUES (
                (SELECT user_id FROM usermaster WHERE full_name = ?),
                ?, ?
            )
            """,
            [
                ("Alice Johnson", "Python", 5),
                ("Alice Johnson", "SQL", 4),
                ("Bob Sharma", "Recruitment", 5),
                ("Charlie Singh", "Python", 3),
                ("Charlie Singh", "DevOps", 4),
                ("Deepa Patel", "Excel", 5),
                ("Deepa Patel", "SQL", 4),
            ],
        )

    conn.commit()
    conn.close()


def run_query(sql: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    """
    Run a SELECT query and return (column_names, rows).
    If it's not SELECT, we execute and return empty rows.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql)
        if sql.strip().lower().startswith("select"):
            rows = cur.fetchall()
            columns = [col[0] for col in cur.description] if cur.description else []
            conn.close()
            return columns, [tuple(r) for r in rows]
        else:
            conn.commit()
            conn.close()
            return [], []
    except Exception as e:
        conn.close()
        raise e


def get_schema_text() -> str:
    """
    Return a human-readable schema description string.
    """
    return """
Tables and Columns:

1) department
   - dept_id (INTEGER, PK)
   - dept_name (TEXT, UNIQUE)

2) usermaster
   - user_id (INTEGER, PK)
   - full_name (TEXT)
   - email (TEXT, UNIQUE)
   - phone (TEXT)
   - dept_id (INTEGER, FK -> department.dept_id)

3) UserSkillAndRatings
   - id (INTEGER, PK)
   - user_id (INTEGER, FK -> usermaster.user_id)
   - skill_name (TEXT)
   - rating (INTEGER)
"""


def auto_detect_schema(db_path: Path = DB_PATH) -> str:
    """
    Auto-detect schema from any SQLite database.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Human-readable schema description
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cur.fetchall()]
    
    schema_lines = ["Tables and Columns:", ""]
    
    for i, table in enumerate(tables, 1):
        schema_lines.append(f"{i}) {table}")
        
        # Get column info for this table
        cur.execute(f"PRAGMA table_info({table});")
        columns = cur.fetchall()
        
        for col in columns:
            col_id, name, col_type, not_null, default_val, is_pk = col
            
            # Build column description
            col_desc = f"   - {name} ({col_type}"
            
            if is_pk:
                col_desc += ", PK"
            if not_null and not is_pk:
                col_desc += ", NOT NULL"
                
            col_desc += ")"
            schema_lines.append(col_desc)
        
        # Get foreign keys
        cur.execute(f"PRAGMA foreign_key_list({table});")
        fks = cur.fetchall()
        
        for fk in fks:
            fk_id, seq, ref_table, from_col, to_col = fk[0:5]
            schema_lines.append(f"   - {from_col} (FK -> {ref_table}.{to_col})")
        
        schema_lines.append("")  # Empty line between tables
    
    conn.close()
    
    return "\n".join(schema_lines)


# Global variable to track current database path
_current_db_path: Path = DB_PATH


def set_database_path(db_path: str) -> bool:
    """
    Set a custom database path.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        True if successful, False otherwise
    """
    global _current_db_path
    
    try:
        path = Path(db_path)
        if not path.exists():
            print(f"Database file not found: {db_path}")
            return False
        
        # Test connection
        conn = sqlite3.connect(path)
        conn.close()
        
        _current_db_path = path
        return True
        
    except Exception as e:
        print(f"Error setting database path: {e}")
        return False


def get_current_database_path() -> Path:
    """Get the current database path."""
    return _current_db_path


def reset_to_default_database():
    """Reset to default database."""
    global _current_db_path
    _current_db_path = DB_PATH
