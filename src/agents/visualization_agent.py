# visualization_agent.py
"""
Visualization Agent - Generates charts and graphs from SQL query results.
Automatically detects appropriate chart types based on data patterns.
"""

import plotly.express as px
import plotly.graph_objects as go
from typing import List, Tuple, Any, Optional, Dict
from .agent_base import Agent
import pandas as pd


class VisualizationAgent(Agent):
    """Agent responsible for generating data visualizations."""
    
    def __init__(self):
        super().__init__(
            name="Visualization Agent",
            role="Generates charts and visualizations from query results"
        )
    
    def get_system_prompt(self) -> str:
        """System prompt for visualization recommendations."""
        return """You are a data visualization expert. Analyze data and recommend the best chart type.

Based on the data structure, recommend ONE of these chart types:
- bar: For categorical comparisons (department names, user counts, etc.)
- pie: For percentage/proportion data (<=7 categories)
- line: For time series or trend data
- scatter: For correlation between two numeric columns
- table: For complex data that doesn't fit other types
- none: If data is not suitable for visualization

Respond with ONLY the chart type (one word), nothing else."""
    
    def process(
        self,
        columns: List[str],
        rows: List[Tuple[Any, ...]],
        sql_query: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Generate visualization from query results.
        
        Args:
            columns: Column names from query result
            rows: Result rows
            sql_query: The SQL query (optional, for context)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with:
            - chart_type: str
            - figure: plotly figure object
            - recommendation: str
            Or None if visualization not possible
        """
        if not rows or len(rows) == 0:
            return None
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(rows, columns=columns)
        
        # Analyze data and determine chart type
        chart_type = self._detect_chart_type(df, columns, sql_query)
        
        if chart_type == "none" or chart_type is None:
            return {
                "chart_type": "none",
                "figure": None,
                "recommendation": "This data is best viewed as a table."
            }
        
        # Generate the chart
        try:
            figure = self._generate_chart(df, chart_type, columns)
            return {
                "chart_type": chart_type,
                "figure": figure,
                "recommendation": self._get_chart_recommendation(chart_type, df)
            }
        except Exception as e:
            print(f"[Visualization Agent] Error generating chart: {e}")
            return {
                "chart_type": "error",
                "figure": None,
                "recommendation": f"Could not generate visualization: {str(e)}"
            }
    
    def _detect_chart_type(
        self, 
        df: pd.DataFrame, 
        columns: List[str],
        sql_query: Optional[str]
    ) -> str:
        """
        Detect the best chart type for the data.
        
        Args:
            df: Data as DataFrame
            columns: Column names
            sql_query: Original SQL query
            
        Returns:
            Chart type string
        """
        num_rows = len(df)
        num_cols = len(columns)
        
        # Not enough data for visualization
        if num_rows < 1 or num_cols < 1:
            return "none"
        
        # Only one row - table is better
        if num_rows == 1 and num_cols > 2:
            return "none"
        
        # Identify column types
        numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
        categorical_cols = [c for c in columns if c not in numeric_cols]
        
        # Check for aggregation keywords in SQL
        is_aggregation = sql_query and any(
            kw in sql_query.upper() 
            for kw in ['COUNT', 'SUM', 'AVG', 'GROUP BY', 'MAX', 'MIN']
        )
        
        # Decision logic
        if num_cols == 2 and len(categorical_cols) == 1 and len(numeric_cols) == 1:
            # One categorical, one numeric → bar or pie
            if num_rows <= 7:
                return "pie"
            else:
                return "bar"
        
        elif num_cols == 2 and len(numeric_cols) == 2:
            # Two numeric columns → scatter plot
            return "scatter"
        
        elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            # Mixed columns → bar chart
            return "bar"
        
        elif is_aggregation:
            # Aggregation query → bar chart
            return "bar"
        
        elif num_rows > 10 and len(numeric_cols) >= 1:
            # Many rows with numeric data → line chart
            return "line"
        
        else:
            # Default to bar if we have categories
            if len(categorical_cols) >= 1:
                return "bar"
            return "none"
    
    def _generate_chart(
        self, 
        df: pd.DataFrame, 
        chart_type: str, 
        columns: List[str]
    ) -> go.Figure:
        """
        Generate a Plotly chart.
        
        Args:
            df: Data as DataFrame
            chart_type: Type of chart to generate
            columns: Column names
            
        Returns:
            Plotly figure object
        """
        # Identify columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
        categorical_cols = [c for c in columns if c not in numeric_cols]
        
        # Default assignments
        x_col = categorical_cols[0] if categorical_cols else columns[0]
        y_col = numeric_cols[0] if numeric_cols else columns[-1]
        
        # Apply modern theme
        template = "plotly_dark"
        
        if chart_type == "bar":
            fig = px.bar(
                df, 
                x=x_col, 
                y=y_col,
                title=f"{y_col} by {x_col}",
                template=template,
                color=x_col,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(showlegend=False)
            
        elif chart_type == "pie":
            fig = px.pie(
                df, 
                names=x_col, 
                values=y_col,
                title=f"Distribution of {y_col}",
                template=template,
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.4  # Donut chart
            )
            
        elif chart_type == "line":
            fig = px.line(
                df, 
                x=x_col if x_col else df.index, 
                y=y_col,
                title=f"{y_col} Trend",
                template=template,
                markers=True
            )
            
        elif chart_type == "scatter":
            if len(numeric_cols) >= 2:
                fig = px.scatter(
                    df, 
                    x=numeric_cols[0], 
                    y=numeric_cols[1],
                    title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                    template=template,
                    trendline="ols" if len(df) > 3 else None
                )
            else:
                fig = px.scatter(
                    df, 
                    x=df.index, 
                    y=y_col,
                    title=f"{y_col} Distribution",
                    template=template
                )
        else:
            # Fallback to bar
            fig = px.bar(df, x=x_col, y=y_col, template=template)
        
        # Common styling
        fig.update_layout(
            font=dict(family="Inter, sans-serif", size=12),
            title_font_size=16,
            margin=dict(l=40, r=40, t=60, b=40),
            height=400
        )
        
        return fig
    
    def _get_chart_recommendation(self, chart_type: str, df: pd.DataFrame) -> str:
        """
        Get a recommendation message for the chart.
        
        Args:
            chart_type: Type of chart generated
            df: Data DataFrame
            
        Returns:
            Recommendation string
        """
        recommendations = {
            "bar": f"Bar chart showing comparison across {len(df)} categories.",
            "pie": f"Pie chart showing distribution of {len(df)} segments.",
            "line": f"Line chart showing trend across {len(df)} data points.",
            "scatter": "Scatter plot showing relationship between variables.",
            "none": "Data is best viewed as a table."
        }
        return recommendations.get(chart_type, "Visualization generated.")


# Singleton instance
_visualization_agent_instance: Optional[VisualizationAgent] = None


def get_visualization_agent() -> VisualizationAgent:
    """Get or create singleton Visualization Agent instance."""
    global _visualization_agent_instance
    if _visualization_agent_instance is None:
        _visualization_agent_instance = VisualizationAgent()
    return _visualization_agent_instance
