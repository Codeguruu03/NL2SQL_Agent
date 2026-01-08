# tests/test_agents.py
"""
Tests for the multi-agent system.
"""
import pytest
from unittest.mock import Mock, patch
import os


class TestSQLAgentUnit:
    """Unit tests for SQL Agent (without LLM calls)."""
    
    def test_sql_agent_validate_query_select(self):
        """Test that SELECT queries are validated as safe."""
        with patch('src.agents.agent_base.get_openrouter_client') as mock:
            mock.return_value = Mock()
            from src.agents.sql_agent import SQLAgent
            agent = SQLAgent()
            
            assert agent.validate_query("SELECT * FROM users;") == True
            assert agent.validate_query("SELECT id, name FROM table;") == True
    
    def test_sql_agent_validate_query_dangerous(self):
        """Test that dangerous queries are blocked."""
        with patch('src.agents.agent_base.get_openrouter_client') as mock:
            mock.return_value = Mock()
            from src.agents.sql_agent import SQLAgent
            agent = SQLAgent()
            
            assert agent.validate_query("DROP TABLE users;") == False
            assert agent.validate_query("DELETE FROM users;") == False
            assert agent.validate_query("INSERT INTO users VALUES (1);") == False
            assert agent.validate_query("UPDATE users SET name='x';") == False
    
    def test_sql_agent_clean_sql_response(self):
        """Test SQL response cleaning."""
        with patch('src.agents.agent_base.get_openrouter_client') as mock:
            mock.return_value = Mock()
            from src.agents.sql_agent import SQLAgent
            agent = SQLAgent()
            
            # Test markdown code block removal
            response = "```sql\nSELECT * FROM users\n```"
            cleaned = agent._clean_sql_response(response)
            assert "```" not in cleaned
            assert "SELECT" in cleaned
            
            # Test whitespace handling
            response = "  SELECT * FROM users;  "
            cleaned = agent._clean_sql_response(response)
            assert cleaned.startswith("SELECT")
            assert cleaned.endswith(";")


class TestSummaryAgentUnit:
    """Unit tests for Summary Agent."""
    
    def test_summary_agent_format_results(self):
        """Test result formatting for LLM."""
        with patch('src.agents.agent_base.get_openrouter_client') as mock:
            mock.return_value = Mock()
            from src.agents.summary_agent import SummaryAgent
            agent = SummaryAgent()
            
            columns = ["id", "name", "value"]
            rows = [(1, "Alice", 100), (2, "Bob", 200)]
            
            result = agent._format_results(columns, rows)
            
            assert "Columns:" in result
            assert "id" in result
            assert "name" in result
            assert "Alice" in result
            assert "Bob" in result
    
    def test_summary_agent_fallback_summary(self):
        """Test fallback summary generation."""
        with patch('src.agents.agent_base.get_openrouter_client') as mock:
            mock.return_value = Mock()
            from src.agents.summary_agent import SummaryAgent
            agent = SummaryAgent()
            
            # Test single row
            summary = agent._generate_fallback_summary("SELECT...", 1)
            assert "1 result" in summary
            
            # Test multiple rows
            summary = agent._generate_fallback_summary("SELECT...", 5)
            assert "5 results" in summary
            
            # Test zero rows
            summary = agent._generate_fallback_summary("SELECT...", 0)
            assert "No results" in summary


class TestVisualizationAgent:
    """Tests for Visualization Agent."""
    
    def test_viz_agent_detect_chart_type_bar(self):
        """Test chart type detection for bar charts."""
        import pandas as pd
        
        with patch('src.agents.agent_base.get_openrouter_client') as mock:
            mock.return_value = Mock()
            from src.agents.visualization_agent import VisualizationAgent
            agent = VisualizationAgent()
            
            # Categorical + numeric = bar chart
            df = pd.DataFrame({
                "dept": ["Engineering", "HR", "Finance"],
                "count": [10, 5, 3]
            })
            
            chart_type = agent._detect_chart_type(df, ["dept", "count"], None)
            
            # Should be bar or pie (both valid for this data)
            assert chart_type in ["bar", "pie"]
    
    def test_viz_agent_detect_chart_type_no_viz(self):
        """Test that complex data returns no visualization."""
        import pandas as pd
        
        with patch('src.agents.agent_base.get_openrouter_client') as mock:
            mock.return_value = Mock()
            from src.agents.visualization_agent import VisualizationAgent
            agent = VisualizationAgent()
            
            # Single row with many columns
            df = pd.DataFrame({
                "a": [1], "b": ["x"], "c": ["y"], "d": ["z"]
            })
            
            chart_type = agent._detect_chart_type(df, ["a", "b", "c", "d"], None)
            
            assert chart_type == "none"
    
    def test_viz_agent_process_empty_data(self):
        """Test processing empty data."""
        with patch('src.agents.agent_base.get_openrouter_client') as mock:
            mock.return_value = Mock()
            from src.agents.visualization_agent import VisualizationAgent
            agent = VisualizationAgent()
            
            result = agent.process(
                columns=["id"],
                rows=[]
            )
            
            assert result is None


class TestOpenRouterClient:
    """Tests for OpenRouter API client."""
    
    def test_client_requires_api_key(self):
        """Test that client raises error without API key."""
        # Remove API key from environment
        old_key = os.environ.pop('OPENROUTER_API_KEY', None)
        
        try:
            from src.core.openrouter_client import OpenRouterClient
            with pytest.raises(ValueError) as exc_info:
                client = OpenRouterClient(api_key=None)
            
            assert "API key is required" in str(exc_info.value)
        finally:
            # Restore key if it existed
            if old_key:
                os.environ['OPENROUTER_API_KEY'] = old_key
    
    def test_client_with_api_key(self):
        """Test that client initializes with API key."""
        from src.core.openrouter_client import OpenRouterClient
        
        client = OpenRouterClient(api_key="test-key-12345")
        
        assert client.api_key == "test-key-12345"
        assert client.model is not None


# Run tests with: pytest tests/test_agents.py -v
