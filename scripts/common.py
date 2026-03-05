#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any
from urllib import error, request


KST = dt.timezone(dt.timedelta(hours=9))


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_paths() -> dict[str, Path]:
    studybot_home = Path(os.environ.get("STUDYBOT_HOME", "/opt/studybot"))
    repo_home = Path(os.environ.get("REPO_HOME", "/opt/repos/daily-study-"))
    return {
        "studybot_home": studybot_home,
        "repo_home": repo_home,
        "env": studybot_home / ".env",
        "topics": studybot_home / "topics.yml",
        "state": studybot_home / "state.json",
        "work_dir": repo_home / "notes" / "work",
        "today_html": repo_home / "public" / "today.html",
    }


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_topics_yaml(text: str) -> list[dict[str, Any]]:
    topics: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_links = False

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if in_links and line.startswith("    - "):
            current.setdefault("reading_links", []).append(_strip_quotes(stripped[2:]))
            continue

        if line.startswith("- "):
            if current:
                topics.append(current)
            current = {}
            in_links = False
            item = line[2:]
            if item:
                if ":" not in item:
                    raise ValueError(f"Invalid topic line: {line}")
                k, v = item.split(":", 1)
                current[k.strip()] = _strip_quotes(v)
            continue

        if current is None:
            raise ValueError("topics.yml must start with '- id: ...'")


        if ":" not in stripped:
            raise ValueError(f"Invalid mapping line: {line}")

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if key == "reading_links":
            current["reading_links"] = []
            in_links = True
            continue

        in_links = False
        current[key] = _strip_quotes(value)

    if current:
        topics.append(current)

    return topics


def load_topics(path: Path) -> list[dict[str, Any]]:
    data = parse_topics_yaml(path.read_text(encoding="utf-8"))
    if not data:
        raise ValueError("topics.yml must be a non-empty YAML list")
    required = {
        "id",
        "title",
        "summary",
        "linux_focus",
        "windows_focus",
        "practice",
        "reading_links",
    }
    for topic in data:
        if not isinstance(topic, dict):
            raise ValueError("Each topic must be a map")
        missing = required - set(topic)
        if missing:
            raise ValueError(f"Topic missing keys: {sorted(missing)}")
        if not isinstance(topic["reading_links"], list):
            raise ValueError("reading_links must be a list")
    return data


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"current_index": 0}
    state = json.loads(path.read_text(encoding="utf-8"))
    if "current_index" not in state or not isinstance(state["current_index"], int):
        raise ValueError("state.json must contain integer 'current_index'")
    return state


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def current_topic(topics: list[dict[str, Any]], state: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    index = state["current_index"] % len(topics)
    return index, topics[index]


def gotify_send(title: str, message: str, *, priority: int = 5) -> None:
    gotify_url = os.environ.get("GOTIFY_URL", "http://localhost:8088")
    token = os.environ.get("GOTIFY_TOKEN")
    if not token:
        raise ValueError("GOTIFY_TOKEN is required in /opt/studybot/.env")
    endpoint = f"{gotify_url.rstrip('/')}/message?token={token}"
    payload = json.dumps({"title": title, "message": message, "priority": priority}).encode("utf-8")
    req = request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=10) as resp:
            if resp.status >= 300:
                raise RuntimeError(f"Gotify returned HTTP {resp.status}")
    except error.URLError as exc:
        raise RuntimeError(f"Gotify request failed: {exc}") from exc


def today_kst() -> str:
    return dt.datetime.now(tz=KST).date().isoformat()
