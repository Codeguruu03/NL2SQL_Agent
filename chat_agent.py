# chat_agent.py
"""
Chat Agent - Main orchestrator for the multi-agent system.
Routes user requests to appropriate agents and coordinates responses.
"""

from typing import Optional, Dict, Any
from agent_base import Agent
from sql_agent import get_sql_agent
from summary_agent import get_summary_agent
from visualization_agent import get_visualization_agent


class ChatAgent(Agent):
    """Orchestrator agent that coordinates other agents."""
    
    def __init__(self):
        super().__init__(
            name="Chat Agent",
            role="Orchestrates SQL, Summary, and Visualization agents to answer user queries"
        )
        self.sql_agent = get_sql_agent()
        self.summary_agent = get_summary_agent()
        self.visualization_agent = get_visualization_agent()
    
    def get_system_prompt(self) -> str:
        """System prompt for chat orchestration."""
        return """You are a helpful database assistant that helps users query their database using natural language.

You coordinate with specialized agents:
- SQL Agent: Converts natural language to SQL queries
- Summary Agent: Interprets query results
- Visualization Agent: Creates charts and graphs

Your job is to:
1. Understand user intent
2. Route requests to the SQL Agent
3. Get results summarized by the Summary Agent
4. Generate visualizations when appropriate
5. Provide helpful, conversational responses

Be friendly, concise, and helpful."""
    
    def process(
        self,
        user_query: str,
        schema: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process user query using multi-agent workflow.
        
        Args:
            user_query: Natural language query from user
            schema: Database schema
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with:
            - success: bool
            - sql_query: str (if successful)
            - columns: list (if successful)
            - rows: list (if successful)
            - summary: str (if successful)
            - visualization: dict (if available)
            - error: str (if failed)
        """
        result = {
            "success": False,
            "sql_query": None,
            "columns": None,
            "rows": None,
            "summary": None,
            "visualization": None,
            "error": None
        }
        
        # Step 1: Use SQL Agent to generate and execute query
        try:
            self.sql_agent.set_schema(schema)
            sql_query, columns, rows = self.sql_agent.process(
                user_query=user_query,
                schema=schema
            )
            
            if sql_query is None:
                result["error"] = (
                    "I couldn't understand your query. "
                    "Please try rephrasing your question or ask for help with examples."
                )
                return result
            
            result["sql_query"] = sql_query
            
            # Check if query executed successfully
            if columns is None or rows is None:
                result["error"] = (
                    "The SQL query was generated but failed to execute. "
                    "There might be an issue with the query or database."
                )
                return result
            
            result["columns"] = columns
            result["rows"] = rows
            
        except Exception as e:
            result["error"] = f"An error occurred while processing your query: {str(e)}"
            return result
        
        # Step 2: Use Summary Agent to generate insights
        try:
            summary = self.summary_agent.process(
                sql_query=sql_query,
                columns=columns,
                rows=rows,
                user_query=user_query
            )
            
            result["summary"] = summary
            
        except Exception as e:
            # Even if summary fails, we still have the results
            result["summary"] = f"Results retrieved successfully, but couldn't generate summary: {str(e)}"
        
        # Step 3: Use Visualization Agent to generate charts
        try:
            viz_result = self.visualization_agent.process(
                columns=columns,
                rows=rows,
                sql_query=sql_query
            )
            
            if viz_result and viz_result.get("figure"):
                result["visualization"] = viz_result
                
        except Exception as e:
            # Visualization is optional, don't fail the whole request
            print(f"[Chat Agent] Visualization failed: {e}")
            result["visualization"] = None
        
        result["success"] = True
        return result
    
    def handle_conversation(
        self,
        user_message: str,
        schema: str
    ) -> str:
        """
        Handle a conversational query (alternative to structured process).
        Returns a simple text response.
        
        Args:
            user_message: User's message
            schema: Database schema
            
        Returns:
            Text response
        """
        result = self.process(user_query=user_message, schema=schema)
        
        if not result["success"]:
            return result.get("error", "An unknown error occurred.")
        
        # Format a conversational response
        response_parts = []
        
        if result.get("summary"):
            response_parts.append(result["summary"])
        
        if result.get("rows"):
            response_parts.append(f"\n\n📊 Found {len(result['rows'])} result(s).")
        
        if result.get("visualization"):
            response_parts.append("\n\n📈 Visualization generated!")
        
        return "\n".join(response_parts) if response_parts else "Query completed."


# Singleton instance
_chat_agent_instance: Optional[ChatAgent] = None


def get_chat_agent() -> ChatAgent:
    """Get or create singleton Chat Agent instance."""
    global _chat_agent_instance
    if _chat_agent_instance is None:
        _chat_agent_instance = ChatAgent()
    return _chat_agent_instance
