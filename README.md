# Multi-Agent SQL Query System 🧠

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-red.svg)](https://streamlit.io)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-API-green.svg)](https://openrouter.ai)

A sophisticated multi-agent AI system that converts natural language queries into SQL, executes them, and provides intelligent insights. Built with three specialized AI agents working collaboratively.

---

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Agent Details](#-agent-details)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Technical Documentation](#-technical-documentation)
- [API Integration](#-api-integration)
- [Troubleshooting](#-troubleshooting)
- [Credits](#-credits)

---

## 🎯 Features

### Multi-Agent Architecture
- **🤖 Chat Agent**: Main orchestrator that coordinates the entire workflow
- **💾 SQL Agent**: LLM-powered natural language to SQL converter
- **📊 Summary Agent**: Generates human-friendly insights from query results

### Intelligent Query Processing
- Convert natural language to SQL queries using AI
- Support for complex queries (joins, aggregations, filtering)
- Automatic schema awareness and adaptation
- Query validation and safety checks

### Flexible Database Connectivity
- Default SQLite database with sample organizational data
- Connect to any custom SQLite database file
- Auto-detect schema from connected databases
- Real-time database switching

### Advanced Features
- AI-generated insights and summaries
- Error handling with helpful messages
- Retry logic for API failures
- Modern tabbed UI for results display
- Real-time query execution

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (Streamlit Web Application)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   Chat Agent                             │
│              (Orchestrator & Router)                     │
└──────────────┬───────────────────────┬──────────────────┘
               │                       │
               ↓                       ↓
    ┌──────────────────┐    ┌──────────────────┐
    │   SQL Agent      │    │  Summary Agent   │
    │                  │    │                  │
    │ - Schema Analysis│    │ - Result Analysis│
    │ - SQL Generation │    │ - Insight Gen.   │
    │ - Query Execution│    │ - Summarization  │
    └────────┬─────────┘    └───────┬──────────┘
             │                      │
             ↓                      ↓
    ┌────────────────────────────────────┐
    │      OpenRouter LLM API            │
    │  (Llama 3.1 8B Instruct - Free)    │
    └────────────────────────────────────┘
             │
             ↓
    ┌────────────────────────────────────┐
    │      SQLite Database               │
    │   (Default or Custom DB)           │
    └────────────────────────────────────┘
```

### Workflow

```
1. User Input (Natural Language)
         ↓
2. Chat Agent receives and validates request
         ↓
3. SQL Agent:
   - Analyzes database schema
   - Generates appropriate SQL query
   - Validates query for safety
   - Executes against database
         ↓
4. Summary Agent:
   - Receives query results
   - Analyzes data patterns
   - Generates natural language summary
         ↓
5. UI displays:
   - Generated SQL query
   - Results table
   - AI-generated insights
```

---

## 🤖 Agent Details

### 1. Chat Agent (`chat_agent.py`)

**Role**: Main orchestrator and coordinator

**Responsibilities**:
- Receives user queries from the UI
- Routes requests to appropriate agents
- Manages agent communication flow
- Handles errors and edge cases
- Returns unified responses to the UI

**Key Methods**:
- `process(user_query, schema)`: Main processing pipeline
- `handle_conversation()`: Alternative conversational interface

---

### 2. SQL Agent (`sql_agent.py`)

**Role**: Natural language to SQL converter

**Responsibilities**:
- Analyzes database schema
- Converts natural language to SQL using LLM
- Validates generated queries for safety
- Executes SQL against the database
- Returns structured results

**Key Features**:
- Lower temperature (0.3) for consistent SQL generation
- Query validation (SELECT-only policy)
- SQL injection prevention
- Automatic schema injection into prompts

**Key Methods**:
- `process(user_query, schema)`: Generate and execute SQL
- `validate_query(sql)`: Safety validation
- `_clean_sql_response()`: Parse LLM output

---

### 3. Summary Agent (`summary_agent.py`)

**Role**: Result interpreter and insight generator

**Responsibilities**:
- Receives SQL query results
- Analyzes data patterns and trends
- Generates human-friendly summaries
- Highlights key findings and insights

**Key Features**:
- Moderate temperature (0.7) for natural language
- Handles large result sets (up to 20 rows)
- Fallback summaries when LLM fails
- Contextual analysis with original query

**Key Methods**:
- `process(sql_query, columns, rows)`: Generate summary
- `_format_results()`: Prepare data for LLM
- `_generate_fallback_summary()`: Backup summary generation

---

## 📁 Project Structure

```
Assignment/
│
├── 🎯 Core Application
│   ├── app.py                    # Streamlit UI and main application
│   └── db.py                     # Database operations and schema detection
│
├── 🤖 Multi-Agent System
│   ├── agent_base.py             # Abstract base class for all agents
│   ├── chat_agent.py             # Orchestrator agent
│   ├── sql_agent.py              # SQL generation agent
│   └── summary_agent.py          # Result interpretation agent
│
├── 🔧 Infrastructure
│   └── openrouter_client.py      # OpenRouter API client wrapper
│
├── ⚙️ Configuration
│   ├── .env                      # Environment variables (API keys)
│   ├── .env.example              # Environment template
│   ├── requirements.txt          # Python dependencies
│   └── .gitignore               # Git ignore rules
│
├── 💾 Data
│   └── test_db.sqlite           # Default SQLite database (auto-created)
│
└── 📚 Documentation
    └── README.md                 # This file
```

### File Descriptions

| File | Lines | Purpose |
|------|-------|---------|
| `app.py` | ~210 | Main Streamlit application with UI and database connectivity |
| `agent_base.py` | ~105 | Base class providing common agent functionality |
| `chat_agent.py` | ~165 | Orchestrator coordinating SQL and Summary agents |
| `sql_agent.py` | ~210 | Natural language to SQL conversion and execution |
| `summary_agent.py` | ~200 | AI-powered result summarization |
| `openrouter_client.py` | ~150 | OpenRouter API client with retry logic |
| `db.py` | ~250 | Database operations, schema detection, connection management |

---

## 📊 Database Schema

### Default Database (`test_db.sqlite`)

The system includes a sample organizational database:

#### Tables

**1. department**
```sql
CREATE TABLE department (
    dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dept_name TEXT NOT NULL UNIQUE
);
```
- Stores organizational departments
- Sample: Engineering, HR, Finance

**2. usermaster**
```sql
CREATE TABLE usermaster (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    dept_id INTEGER,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);
```
- Stores user/employee information
- Links to departments via foreign key
- Sample: Alice Johnson, Bob Sharma, etc.

**3. UserSkillAndRatings**
```sql
CREATE TABLE UserSkillAndRatings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    rating INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES usermaster(user_id)
);
```
- Stores user skills and proficiency ratings (1-5)
- Sample: Python (5), SQL (4), etc.

#### Sample Data

| Table | Rows | Description |
|-------|------|-------------|
| department | 3 | Engineering, HR, Finance |
| usermaster | 4 | Alice, Bob, Charlie, Deepa |
| UserSkillAndRatings | 7 | Various skills with ratings |

### Custom Databases

The system supports **any SQLite database** through:
- Auto-schema detection using `PRAGMA` queries
- Dynamic table and column discovery
- Foreign key relationship mapping
- Automatic schema formatting for LLM context

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Internet connection (for OpenRouter API)
- OpenRouter API key (free tier available)

### Installation

**Step 1: Clone/Download the Project**
```bash
cd Assignment
```

**Step 2: Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate
```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

Dependencies installed:
- `streamlit` - Web UI framework
- `pandas` - Data manipulation
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management

**Step 4: Configure API Key**

1. Get free API key from [OpenRouter](https://openrouter.ai/)
2. Copy the template:
   ```bash
   copy .env.example .env
   ```
3. Edit `.env` and add your key:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-your_actual_key_here
   OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
   ```

**Step 5: Run the Application**
```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

---

## 💬 Usage Examples

### Example 1: Basic User Query
```
Query: "list all users"

Generated SQL:
SELECT u.user_id, u.full_name, u.email, d.dept_name 
FROM usermaster u 
LEFT JOIN department d ON u.dept_id = d.dept_id;

Results: 4 rows

Summary: "The database contains 4 users across 3 departments. 
Engineering has the most employees with 2 users, while HR and 
Finance each have 1 user."
```

### Example 2: Department Filter
```
Query: "show users in engineering department"

Generated SQL:
SELECT u.user_id, u.full_name, u.email, d.dept_name 
FROM usermaster u 
JOIN department d ON u.dept_id = d.dept_id 
WHERE d.dept_name = 'Engineering';

Results: 2 rows (Alice Johnson, Charlie Singh)

Summary: "The Engineering department has 2 employees: Alice Johnson 
and Charlie Singh. Both are active users in the system."
```

### Example 3: Aggregation Query
```
Query: "what's the average rating for python skill"

Generated SQL:
SELECT s.skill_name, AVG(s.rating) AS avg_rating 
FROM UserSkillAndRatings s 
WHERE s.skill_name = 'Python' 
GROUP BY s.skill_name;

Results: 1 row (Python, 4.0)

Summary: "Python has an average rating of 4.0 across all users. 
This indicates strong proficiency in Python among the team."
```

### Example 4: Complex Query
```
Query: "which department has the most skilled employees"

Generated SQL:
SELECT d.dept_name, COUNT(DISTINCT s.user_id) as skilled_count
FROM department d
JOIN usermaster u ON d.dept_id = u.dept_id
JOIN UserSkillAndRatings s ON u.user_id = s.user_id
GROUP BY d.dept_name
ORDER BY skilled_count DESC;
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | ✅ Yes | - | Your OpenRouter API key |
| `OPENROUTER_MODEL` | ❌ No | `meta-llama/llama-3.1-8b-instruct:free` | LLM model to use |

### Agent Configuration

Modify these parameters in agent files:

**SQL Agent** (`sql_agent.py`):
```python
temperature=0.3      # Lower for consistent SQL
max_tokens=500       # SQL query length limit
```

**Summary Agent** (`summary_agent.py`):
```python
temperature=0.7      # Higher for natural language
max_tokens=500       # Summary length limit
```

### Database Configuration

**Default Database**: `test_db.sqlite` (auto-created)

**Custom Database**: Use UI sidebar to connect to any SQLite file

---

## 📚 Technical Documentation

### Agent Communication Protocol

Agents communicate through structured dictionaries:

```python
# SQL Agent Output
{
    "sql_query": str,      # Generated SQL
    "columns": List[str],  # Column names
    "rows": List[Tuple]    # Result rows
}

# Summary Agent Output
{
    "summary": str         # Natural language summary
}

# Chat Agent Response
{
    "success": bool,
    "sql_query": str,
    "columns": List[str],
    "rows": List[Tuple],
    "summary": str,
    "error": str | None
}
```

### Error Handling

**Levels**:
1. **API Level**: OpenRouter client with 3 retries
2. **Agent Level**: Try-catch with fallback behaviors
3. **UI Level**: User-friendly error messages

**Example**:
```python
try:
    result = chat_agent.process(query, schema)
except ValueError as e:
    # Configuration error (missing API key)
except Exception as e:
    # Runtime error (API failure, etc.)
```

### Safety Features

**Query Validation**:
- Only SELECT queries allowed
- Blocks: DROP, DELETE, INSERT, UPDATE, ALTER, CREATE
- SQL injection prevention through validation

**Rate Limiting**:
- OpenRouter free tier: Check current limits
- Retry logic with exponential backoff
- Graceful degradation to fallback summaries

---

## 🔌 API Integration

### OpenRouter API

**Endpoint**: `https://openrouter.ai/api/v1/chat/completions`

**Model Used**: `meta-llama/llama-3.1-8b-instruct:free`
- Free tier available
- 8B parameters
- Instruction-tuned for tasks

**Request Format**:
```python
{
    "model": "meta-llama/llama-3.1-8b-instruct:free",
    "messages": [
        {"role": "system", "content": "System prompt..."},
        {"role": "user", "content": "User query..."}
    ],
    "temperature": 0.7,
    "max_tokens": 500
}
```

**Alternative Models**:
Update in `.env`:
```env
OPENROUTER_MODEL=anthropic/claude-3-haiku
OPENROUTER_MODEL=google/gemini-flash-1.5
```

---

## 🐛 Troubleshooting

### Common Issues

**1. API Key Error**
```
ValueError: OpenRouter API key is required
```
**Solution**: Add your API key to `.env` file

**2. Summary Truncated**
```
Summary: "The database contains..."  (cuts off)
```
**Solution**: Already fixed! `max_tokens` increased to 500

**3. App Won't Start**
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution**: Install dependencies: `pip install -r requirements.txt`

**4. Database Connection Failed**
```
Error: Database file not found
```
**Solution**: Check file path or use default database

**5. Empty Results**
```
No results found
```
**Solution**: Normal - query returned no matching records

### Debug Mode

Check terminal output for detailed logs:
```
[OpenRouter] Calling API with model: meta-llama/...
[OpenRouter] Response status: 200
[OpenRouter] Success! Response length: 245 chars
[Summary Agent] Calling LLM with prompt length: 523
[Summary Agent] Successfully generated summary: 245 chars
```

---

## 🛡️ Security & Best Practices

### Security Features
- ✅ API keys stored in `.env` (gitignored)
- ✅ SELECT-only query policy
- ✅ SQL injection prevention
- ✅ Input validation and sanitization
- ✅ No direct database modification allowed

### Best Practices
- Keep API keys confidential
- Use virtual environments
- Regularly update dependencies
- Test with sample databases first
- Monitor API usage and costs

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Multi-agent AI system design
- ✅ LLM integration and prompt engineering
- ✅ Natural language processing for SQL
- ✅ Streamlit web application development
- ✅ API client implementation with error handling
- ✅ Database schema introspection
- ✅ Agent coordination and orchestration
- ✅ Singleton pattern for resource management

---

## 🙏 Credits

**Technologies**:
- [OpenRouter](https://openrouter.ai) - LLM API gateway
- [Streamlit](https://streamlit.io) - Web UI framework
- [SQLite](https://sqlite.org) - Database engine
- [Python](https://python.org) - Programming language

**LLM Model**:
- Meta Llama 3.1 8B Instruct (via OpenRouter)

**Developed By**: Internship Assignment Project

---

## 📄 License

This is an educational project developed for learning purposes.

---

## 🔗 Quick Links

- 🌐 [OpenRouter Dashboard](https://openrouter.ai/dashboard)
- 📖 [Streamlit Documentation](https://docs.streamlit.io)
- 💬 [SQLite Documentation](https://www.sqlite.org/docs.html)
- 🤖 [Llama 3.1 Model Card](https://huggingface.co/meta-llama)

---

**Made with ❤️ using AI and Multi-Agent Systems**
