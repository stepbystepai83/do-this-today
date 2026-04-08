import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_prompt(goal: str, weakness: str, notes: str, history_text: str) -> str:
    return f"""
You are a strict but intelligent action coach.

Your job is to decide the 3 most important actions the user should take TODAY.

User profile:
- Main goal: {goal}
- Main weakness: {weakness}
- Additional notes: {notes}

Recent behavior:
{history_text}

Rules:
1. Output exactly 3 actions.
2. Each action must be specific and actionable.
3. Each action must take less than 60 minutes.
4. Each action must help the user become stronger, more disciplined, or more effective.
5. Include a short reason for each action.
6. Be decisive. No multiple options.
7. Return valid JSON only.

JSON format:
{{
  "actions": [
    {{
      "title": "action title",
      "reason": "short reason",
      "estimated_minutes": 30
    }},
    {{
      "title": "action title",
      "reason": "short reason",
      "estimated_minutes": 20
    }},
    {{
      "title": "action title",
      "reason": "short reason",
      "estimated_minutes": 40
    }}
  ]
}}
""".strip()


def generate_today_actions(goal: str, weakness: str, notes: str, history_text: str) -> list[dict[str, Any]]:
    prompt = build_prompt(goal, weakness, notes, history_text)

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )

    text = response.output_text.strip()

    try:
        parsed = json.loads(text)
        actions = parsed.get("actions", [])
        if len(actions) != 3:
            raise ValueError("Model did not return exactly 3 actions.")
        return actions
    except Exception as e:
        raise ValueError(f"AI 回傳格式解析失敗：{e}\n\n原始內容：\n{text}")