# nlp_to_sql.py
"""
Very simple, rule-based "NLP to SQL" converter.

⚠️ This is NOT a real AI agent.
It only supports a few hard-coded patterns and will fail for many queries.
That's intentional for your assignment requirement ("does not work properly").
"""

import re
from typing import Optional


def text_to_sql(user_text: str) -> Optional[str]:
    """
    Convert a simple English request into a SQL query.

    Supported examples:

    - "list all users"
    - "show all departments"
    - "show users in engineering department"
    - "show users in HR"
    - "show skills of alice johnson"
    - "show average rating for skill python"
    """
    text = user_text.strip().lower()

    # 1) list all users
    if "all users" in text or "list users" in text or "show users" in text:
        # Could be more specific: "show all users"
        return (
            "SELECT u.user_id, u.full_name, u.email, d.dept_name "
            "FROM usermaster u "
            "LEFT JOIN department d ON u.dept_id = d.dept_id;"
        )

    # 2) list all departments
    if "all departments" in text or "list departments" in text:
        return "SELECT dept_id, dept_name FROM department;"

    # 3) users in a specific department (e.g. "users in engineering department")
    if "users in" in text and "department" in text:
        # try to capture the word between 'in' and 'department'
        match = re.search(r"users in (.+?) department", text)
        if match:
            dept_name = match.group(1).strip().title()
            return (
                "SELECT u.user_id, u.full_name, u.email, d.dept_name "
                "FROM usermaster u "
                "JOIN department d ON u.dept_id = d.dept_id "
                f"WHERE d.dept_name = '{dept_name}';"
            )

    # simpler: "users in engineering"
    if "users in" in text:
        match = re.search(r"users in (.+)$", text)
        if match:
            dept_name = match.group(1).strip().title()
            return (
                "SELECT u.user_id, u.full_name, u.email, d.dept_name "
                "FROM usermaster u "
                "JOIN department d ON u.dept_id = d.dept_id "
                f"WHERE d.dept_name = '{dept_name}';"
            )

    # 4) show skills of a user  ("skills of alice", "skills for alice johnson")
    if "skills of" in text or "skills for" in text:
        # capture name after "skills of/for"
        match = re.search(r"skills (?:of|for) (.+)$", text)
        if match:
            full_name = match.group(1).strip().title()
            return (
                "SELECT u.full_name, s.skill_name, s.rating "
                "FROM usermaster u "
                "JOIN UserSkillAndRatings s ON u.user_id = s.user_id "
                f"WHERE u.full_name = '{full_name}';"
            )

    # 5) average rating for a skill ("average rating for skill python")
    if "average rating" in text and "skill" in text:
        match = re.search(r"average rating.*skill (.+)$", text)
        if match:
            skill = match.group(1).strip().title()
            return (
                "SELECT s.skill_name, AVG(s.rating) AS avg_rating "
                "FROM UserSkillAndRatings s "
                f"WHERE s.skill_name = '{skill}' "
                "GROUP BY s.skill_name;"
            )

    # If nothing matched, return None to signal "I don't understand"
    return None
