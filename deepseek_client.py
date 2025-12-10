import requests
import re

DEEPSEEK_API_KEY = "sk-2d5102e826194c769708a74af5ac724f"  # your real key here

API_URL = "https://api.deepseek.com/chat/completions"


def _strip_code_fences(text: str) -> str:
    """
    Remove ```sql ... ``` or ``` ... ``` fences if present.
    """
    text = text.strip()

    # Try to extract content inside ``` ``` or ```sql ```
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: just return original stripped text
    return text


def generate_sql_from_deepseek(user_text: str, schema_text: str) -> str | None:
    if not DEEPSEEK_API_KEY:
        return None

    prompt = f"""
You are a SQL query generator.
Database schema:
{schema_text}

User request: "{user_text}"

Rules:
- Output ONLY the SQL query.
- Do NOT explain anything.
- Prefer not to wrap it in markdown, but if you do, use ```sql ... ``` and nothing else.
"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        raw_sql = content.strip()
        clean_sql = _strip_code_fences(raw_sql)
        print("RAW FROM LLM:\n", raw_sql)
        print("CLEAN SQL:\n", clean_sql)
        return clean_sql
    except Exception as e:
        print("DeepSeek Error:", e)
        return None


if __name__ == "__main__":
    # quick test
    from db import get_schema_text
    sql = generate_sql_from_deepseek("list all users", get_schema_text())
    print("FINAL SQL TO EXECUTE:\n", sql)