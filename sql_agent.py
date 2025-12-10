# sql_agent.py
"""
SQL Agent - Generates and executes SQL queries from natural language.
Uses LLM to convert user requests into SQL queries based on database schema.
"""

import re
from typing import Optional, Tuple, List, Any
from agent_base import Agent
from db import get_connection, run_query


class SQLAgent(Agent):
    """Agent responsible for generating and executing SQL queries."""
    
    def __init__(self):
        super().__init__(
            name="SQL Agent",
            role="Converts natural language to SQL queries and executes them"
        )
        self.current_schema: Optional[str] = None
    
    def get_system_prompt(self) -> str:
        """System prompt for SQL generation."""
        return """You are an expert SQL query generator. Your job is to:

1. Analyze the user's natural language request
2. Examine the provided database schema
3. Generate a valid SQL query that answers the user's question
4. Return ONLY the SQL query, nothing else

Rules:
- Generate SQLite-compatible SQL queries only
- Use proper JOIN syntax when needed
- Use appropriate WHERE clauses for filtering
- For aggregations, use GROUP BY when necessary
- Return only SELECT queries (no INSERT, UPDATE, DELETE)
- Do NOT include explanations or markdown formatting
- Do NOT include ```sql``` code blocks
- Return just the raw SQL query

Example:
User: "show all users"
Schema: usermaster(user_id, full_name, email)
Output: SELECT * FROM usermaster;"""
    
    def set_schema(self, schema: str):
        """
        Set the database schema for SQL generation.
        
        Args:
            schema: Database schema description
        """
        self.current_schema = schema
    
    def process(
        self,
        user_query: str,
        schema: Optional[str] = None,
        **kwargs
    ) -> Tuple[Optional[str], Optional[List[str]], Optional[List[Tuple[Any, ...]]]]:
        """
        Process natural language query and return SQL + results.
        
        Args:
            user_query: Natural language query from user
            schema: Database schema (optional, uses current_schema if not provided)
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (sql_query, column_names, rows)
            Returns (None, None, None) on failure
        """
        # Use provided schema or fallback to current_schema
        schema_to_use = schema or self.current_schema
        
        if not schema_to_use:
            print("Error: No database schema provided")
            return None, None, None
        
        # Generate SQL query
        sql_query = self._generate_sql(user_query, schema_to_use)
        
        if not sql_query:
            print("Error: Failed to generate SQL query")
            return None, None, None
        
        # Validate it's a SELECT query
        if not sql_query.strip().upper().startswith("SELECT"):
            print("Error: Only SELECT queries are allowed")
            return None, None, None
        
        # Execute query
        try:
            columns, rows = run_query(sql_query)
            return sql_query, columns, rows
        except Exception as e:
            print(f"Error executing SQL: {e}")
            return sql_query, None, None
    
    def _generate_sql(self, user_query: str, schema: str) -> Optional[str]:
        """
        Generate SQL query from natural language.
        
        Args:
            user_query: Natural language query
            schema: Database schema
            
        Returns:
            Generated SQL query or None on failure
        """
        # Create prompt with schema and user query
        prompt = f"""Database Schema:
{schema}

User Request: {user_query}

Generate a SQL query to answer this request. Return ONLY the SQL query."""
        
        # Call LLM
        response = self.call_llm(
            user_message=prompt,
            temperature=0.3,  # Lower temperature for more consistent SQL
            max_tokens=500
        )
        
        if not response:
            return None
        
        # Clean up the response
        sql_query = self._clean_sql_response(response)
        
        return sql_query
    
    def _clean_sql_response(self, response: str) -> str:
        """
        Clean LLM response to extract pure SQL.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Cleaned SQL query
        """
        # Remove markdown code blocks if present
        sql = response.strip()
        
        # Remove ```sql and ``` markers
        sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'```\s*$', '', sql)
        
        # Remove leading/trailing whitespace
        sql = sql.strip()
        
        # Remove any explanatory text before the query
        # Look for SELECT keyword and take from there
        match = re.search(r'(SELECT\s+.*)', sql, re.IGNORECASE | re.DOTALL)
        if match:
            sql = match.group(1)
        
        # Remove semicolon at the end if present (optional)
        sql = sql.rstrip(';').strip()
        
        # Add semicolon back for consistency
        sql = sql + ';'
        
        return sql
    
    def validate_query(self, sql: str) -> bool:
        """
        Validate SQL query for safety.
        
        Args:
            sql: SQL query to validate
            
        Returns:
            True if query is safe, False otherwise
        """
        # Convert to uppercase for checking
        sql_upper = sql.upper().strip()
        
        # Only allow SELECT queries
        if not sql_upper.startswith("SELECT"):
            return False
        
        # Block dangerous keywords
        dangerous_keywords = [
            "DROP", "DELETE", "INSERT", "UPDATE", 
            "ALTER", "CREATE", "TRUNCATE", "EXEC"
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        return True


# Singleton instance
_sql_agent_instance: Optional[SQLAgent] = None


def get_sql_agent() -> SQLAgent:
    """Get or create singleton SQL Agent instance."""
    global _sql_agent_instance
    if _sql_agent_instance is None:
        _sql_agent_instance = SQLAgent()
    return _sql_agent_instance
