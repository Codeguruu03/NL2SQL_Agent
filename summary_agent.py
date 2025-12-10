# summary_agent.py
"""
Summary Agent - Interprets SQL query results and generates human-friendly summaries.
Takes raw data and provides insights in natural language.
"""

from typing import List, Tuple, Any, Optional
from agent_base import Agent


class SummaryAgent(Agent):
    """Agent responsible for summarizing query results."""
    
    def __init__(self):
        super().__init__(
            name="Summary Agent",
            role="Interprets SQL results and generates natural language summaries"
        )
    
    def get_system_prompt(self) -> str:
        """System prompt for summary generation."""
        return """You are a data analyst who explains query results in clear, natural language.

Your job is to:
1. Analyze the SQL query results
2. Identify key insights and patterns
3. Generate a concise, human-friendly summary
4. Highlight important findings

Guidelines:
- Be concise but informative (2-4 sentences)
- Use natural, conversational language
- Mention specific numbers/values when relevant
- Point out interesting patterns or notable findings
- Don't just list the data - provide insights
- Format the summary clearly

Example:
Query: "SELECT COUNT(*) FROM usermaster"
Results: [(5,)]
Summary: "The database contains 5 users in total. This represents the complete user base across all departments."

Example:
Query: "SELECT dept_name, COUNT(*) FROM usermaster JOIN department..."
Results: [("Engineering", 3), ("HR", 1), ("Finance", 1)]
Summary: "The Engineering department has the most users with 3 people, while HR and Finance each have 1 user. Engineering makes up 60% of the total workforce."
"""
    
    def process(
        self,
        sql_query: str,
        columns: List[str],
        rows: List[Tuple[Any, ...]],
        user_query: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """
        Generate summary from SQL query results.
        
        Args:
            sql_query: The SQL query that was executed
            columns: Column names from the query result
            rows: Result rows
            user_query: Original user query (optional)
            **kwargs: Additional parameters
            
        Returns:
            Natural language summary or None on failure
        """
        # Handle empty results
        if not rows or len(rows) == 0:
            return "No results were found for this query. The database might not contain matching records."
        
        # Format results for the LLM
        results_text = self._format_results(columns, rows)
        
        # Generate summary
        summary = self._generate_summary(
            sql_query=sql_query,
            results_text=results_text,
            user_query=user_query,
            row_count=len(rows)
        )
        
        return summary
    
    def _format_results(
        self,
        columns: List[str],
        rows: List[Tuple[Any, ...]],
        max_rows: int = 20
    ) -> str:
        """
        Format query results as text for the LLM.
        
        Args:
            columns: Column names
            rows: Result rows
            max_rows: Maximum rows to include in formatting
            
        Returns:
            Formatted results text
        """
        # Limit rows to avoid token overflow
        display_rows = rows[:max_rows]
        has_more = len(rows) > max_rows
        
        # Build text representation
        lines = []
        lines.append(f"Columns: {', '.join(columns)}")
        lines.append(f"Total rows: {len(rows)}")
        lines.append("\nData:")
        
        for i, row in enumerate(display_rows):
            row_dict = dict(zip(columns, row))
            lines.append(f"  Row {i+1}: {row_dict}")
        
        if has_more:
            lines.append(f"  ... and {len(rows) - max_rows} more rows")
        
        return "\n".join(lines)
    
    def _generate_summary(
        self,
        sql_query: str,
        results_text: str,
        user_query: Optional[str],
        row_count: int
    ) -> Optional[str]:
        """
        Generate natural language summary using LLM.
        
        Args:
            sql_query: SQL query that was executed
            results_text: Formatted results
            user_query: Original user query
            row_count: Number of result rows
            
        Returns:
            Generated summary or None on failure
        """
        # Build prompt
        prompt_parts = []
        
        if user_query:
            prompt_parts.append(f"User's Question: {user_query}")
        
        prompt_parts.append(f"SQL Query:\n{sql_query}")
        prompt_parts.append(f"\nQuery Results:\n{results_text}")
        prompt_parts.append(
            "\nProvide a clear, insightful summary of these results in 2-4 sentences. "
            "Focus on key findings and patterns."
        )
        
        prompt = "\n\n".join(prompt_parts)
        
        # Call LLM with error handling
        try:
            print(f"[Summary Agent] Calling LLM with prompt length: {len(prompt)}")
            summary = self.call_llm(
                user_message=prompt,
                temperature=0.7,  # Moderate temperature for natural language
                max_tokens=500  # Increased to prevent truncation
            )
            
            if summary:
                print(f"[Summary Agent] Successfully generated summary: {len(summary)} chars")
                return summary
            else:
                print("[Summary Agent] LLM returned None - generating fallback summary")
                # Generate a simple fallback summary
                return self._generate_fallback_summary(sql_query, row_count)
                
        except Exception as e:
            print(f"[Summary Agent] Error generating summary: {e}")
            return self._generate_fallback_summary(sql_query, row_count)
    
    def _generate_fallback_summary(self, sql_query: str, row_count: int) -> str:
        """
        Generate a simple fallback summary when LLM fails.
        
        Args:
            sql_query: SQL query executed
            row_count: Number of rows returned
            
        Returns:
            Basic summary string
        """
        if row_count == 0:
            return "No results found for this query."
        elif row_count == 1:
            return f"The query returned 1 result. The data shows the information matching your request."
        else:
            return f"The query successfully returned {row_count} results. You can see the detailed data in the Results tab above."


# Singleton instance
_summary_agent_instance: Optional[SummaryAgent] = None


def get_summary_agent() -> SummaryAgent:
    """Get or create singleton Summary Agent instance."""
    global _summary_agent_instance
    if _summary_agent_instance is None:
        _summary_agent_instance = SummaryAgent()
    return _summary_agent_instance
