# app.py
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.db import (
    init_db, 
    auto_detect_schema, 
    set_database_path, 
    get_current_database_path,
    reset_to_default_database
)


def main():
    st.set_page_config(
        page_title="Multi-Agent SQL Query System", 
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 Multi-Agent SQL Query System")
    
    st.markdown("""
    This app uses **four specialized AI agents** to help you query databases:
    - 🤖 **Chat Agent**: Orchestrates your requests
    - 💾 **SQL Agent**: Converts natural language to SQL
    - 📊 **Summary Agent**: Interprets results and provides insights
    - 📈 **Visualization Agent**: Auto-generates charts and graphs
    """)
    
    # Initialize session state
    if "db_connected" not in st.session_state:
        st.session_state.db_connected = False
        st.session_state.current_schema = None
        st.session_state.db_name = "Default Database (test_db.sqlite)"
        st.session_state.query_history = []
    
    # Sidebar for database connection
    with st.sidebar:
        st.header("⚙️ Database Settings")
        
        db_option = st.radio(
            "Choose database:",
            ["Default Database", "Custom SQLite File"]
        )
        
        if db_option == "Default Database":
            if st.button("Initialize Default Database"):
                with st.spinner("Initializing default database..."):
                    reset_to_default_database()
                    init_db()
                    st.session_state.current_schema = auto_detect_schema()
                    st.session_state.db_connected = True
                    st.session_state.db_name = "Default Database (test_db.sqlite)"
                    st.success("✅ Default database initialized!")
        
        else:  # Custom SQLite File
            st.info("Enter the path to your SQLite database file")
            
            custom_path = st.text_input(
                "Database Path:",
                placeholder="C:\\path\\to\\your\\database.sqlite"
            )
            
            if st.button("Connect to Database"):
                if custom_path:
                    with st.spinner("Connecting to database..."):
                        if set_database_path(custom_path):
                            try:
                                st.session_state.current_schema = auto_detect_schema(Path(custom_path))
                                st.session_state.db_connected = True
                                st.session_state.db_name = Path(custom_path).name
                                st.success(f"✅ Connected to {Path(custom_path).name}")
                            except Exception as e:
                                st.error(f"Error detecting schema: {e}")
                        else:
                            st.error("Failed to connect. Check the file path.")
                else:
                    st.warning("Please enter a database path")
        
        # Display connection status
        st.divider()
        if st.session_state.db_connected:
            st.success(f"🟢 Connected: {st.session_state.db_name}")
        else:
            st.warning("🔴 Not connected")
    
    # Main content area
    if not st.session_state.db_connected:
        st.info("👈 Please connect to a database using the sidebar to get started.")
        
        # Show example
        with st.expander("ℹ️ How to use this app"):
            st.markdown("""
            1. **Connect to a database** (sidebar)
               - Use the default database with sample data, or
               - Connect to your own SQLite database file
            
            2. **Ask questions in natural language**
               - "List all users"
               - "Show users in the engineering department"
               - "What's the average rating for Python skill?"
            
            3. **View results**
               - See the generated SQL query
               - Browse the data table
               - Read the AI-generated insights
            """)
        return
    
    # Show database schema
    with st.expander("📚 Database Schema (auto-detected)"):
        st.code(st.session_state.current_schema, language="text")
    
    # Query input
    st.subheader("💬 Ask Your Question")
    
    user_query = st.text_area(
        "Type your query in natural language:",
        height=100,
        placeholder="Example: show all users in the engineering department"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.button("🚀 Generate & Run", type="primary")
    with col2:
        if st.button("🔄 Clear"):
            st.rerun()
    
    if submit_button:
        if not user_query.strip():
            st.warning("Please enter a query first.")
            return
        
        # Check if API key is configured
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key == "your_openrouter_api_key_here":
            st.error("🔑 **OpenRouter API Key Not Configured**")
            st.markdown("""
            To use the multi-agent system, you need to set up your OpenRouter API key:
            
            1. **Get a free API key**: Visit [openrouter.ai](https://openrouter.ai/) and sign up
            2. **Update your `.env` file**: 
               - Open the `.env` file in the project directory
               - Replace `your_openrouter_api_key_here` with your actual API key
               - Save the file
            3. **Refresh this page** (the app will reload automatically)
            
            Your `.env` file should look like:
            ```
            OPENROUTER_API_KEY=sk-or-v1-your_actual_key_here
            OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
            ```
            """)
            return
        
        # Show agent working
        with st.spinner("🤖 Agents are working on your request..."):
            try:
                # Lazy import to avoid initialization errors
                from src.agents.chat_agent import get_chat_agent
                
                # Get chat agent and process
                chat_agent = get_chat_agent()
                result = chat_agent.process(
                    user_query=user_query,
                    schema=st.session_state.current_schema
                )
            except ValueError as e:
                st.error(f"❌ Configuration Error: {str(e)}")
                st.info("Please check your `.env` file and ensure the API key is set correctly.")
                return
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return
        
        # Display results
        if not result["success"]:
            st.error(result.get("error", "Unknown error occurred"))
            return
        
        # Success - show all outputs
        st.success("✅ Query processed successfully!")
        
        # Save to query history
        st.session_state.query_history.append({
            "query": user_query,
            "sql": result["sql_query"],
            "rows": len(result["rows"]) if result["rows"] else 0
        })
        
        # Tab layout for organized display
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Results", "📈 Visualization", "💻 SQL Query", "🔍 Insights"])
        
        with tab1:
            st.subheader("Query Results")
            if result["rows"]:
                df = pd.DataFrame(result["rows"], columns=result["columns"])
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total rows: {len(result['rows'])}")
                
                # Export to CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("No results found.")
        
        with tab2:
            st.subheader("Data Visualization")
            if result.get("visualization") and result["visualization"].get("figure"):
                st.plotly_chart(
                    result["visualization"]["figure"], 
                    use_container_width=True
                )
                st.caption(f"📈 {result['visualization'].get('recommendation', 'Chart generated by Visualization Agent')}")
            else:
                st.info("No visualization available for this data. Try queries with aggregations or comparisons.")
            st.caption("🤖 Generated by Visualization Agent")
        
        with tab3:
            st.subheader("Generated SQL Query")
            st.code(result["sql_query"], language="sql")
            st.caption("🤖 Generated by SQL Agent")
        
        with tab4:
            st.subheader("AI Summary & Insights")
            if result["summary"]:
                st.markdown(result["summary"])
            else:
                st.info("No summary available.")
            st.caption("🤖 Generated by Summary Agent")
        
        # Show query history in sidebar
        if st.session_state.query_history:
            with st.sidebar:
                st.divider()
                st.subheader("📜 Query History")
                for i, h in enumerate(reversed(st.session_state.query_history[-5:]), 1):
                    with st.expander(f"{i}. {h['query'][:30]}..."):
                        st.code(h['sql'], language='sql')
                        st.caption(f"Returned {h['rows']} rows")


if __name__ == "__main__":
    main()
