import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict

DATA_FILE = "data.json"


def default_data() -> Dict[str, Any]:
    return {
        "profile": {
            "goal": "",
            "weakness": "",
            "notes": ""
        },
        "history": [],
        "last_tasks": [],
        "streak": {
            "current": 0,
            "last_completed_date": ""
        }
    }


def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        data = default_data()
        save_data(data)
        return data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_profile(goal: str, weakness: str, notes: str) -> None:
    data = load_data()
    data["profile"]["goal"] = goal
    data["profile"]["weakness"] = weakness
    data["profile"]["notes"] = notes
    save_data(data)


def save_tasks(tasks: list[dict]) -> None:
    data = load_data()
    data["last_tasks"] = tasks
    save_data(data)


def get_last_tasks() -> list[dict]:
    data = load_data()
    return data.get("last_tasks", [])


def add_history_entry(entry: Dict[str, Any]) -> None:
    data = load_data()
    data["history"].append(entry)
    data["history"] = data["history"][-30:]
    save_data(data)


def get_recent_history_text() -> str:
    data = load_data()
    history = data.get("history", [])[-7:]

    if not history:
        return "No recent history."

    lines = []
    for item in history:
        date = item.get("date", "")
        completed = item.get("completed_actions", [])
        skipped = item.get("skipped_actions", [])
        lines.append(
            f"{date}: completed={completed}; skipped={skipped}; reflection={item.get('reflection', '')}"
        )
    return "\n".join(lines)


def update_streak_if_completed_today() -> int:
    data = load_data()
    streak = data["streak"]

    today = datetime.now().date()
    last_date_str = streak.get("last_completed_date", "")

    if last_date_str:
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
    else:
        last_date = None

    if last_date == today:
        return streak["current"]

    if last_date == today - timedelta(days=1):
        streak["current"] += 1
    else:
        streak["current"] = 1

    streak["last_completed_date"] = today.strftime("%Y-%m-%d")
    save_data(data)
    return streak["current"]


def get_streak() -> int:
    data = load_data()
    return data.get("streak", {}).get("current", 0)