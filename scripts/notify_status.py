#!/usr/bin/env python3
import json
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = BASE_DIR / "state.json"
WORK_DIR = BASE_DIR / "notes" / "work"
REPO_WEB_BASE = "https://github.com/weeeeestern/daily-study/blob/main"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def load_state():
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_topic_id_from_file(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("TOPIC_ID: "):
            return line.split(": ", 1)[1].strip()
    return None


def find_latest_work_file(topic_id: str):
    matches = sorted(WORK_DIR.glob(f"*-{slugify(topic_id)}.md"))
    return matches[-1] if matches else None


def read_title(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def github_link(path: Path):
    rel = path.relative_to(BASE_DIR).as_posix()
    return f"{REPO_WEB_BASE}/{rel}"


def main():
    state = load_state()
    topic_id = state.get("current_topic_id")
    if not topic_id:
        print("오늘 공부 주제를 아직 찾지 못했어. 조금 있다 다시 불러줘.")
        return

    work_file = find_latest_work_file(topic_id)
    if not work_file:
        print(f"현재 주제 파일이 아직 없어. topic_id={topic_id}")
        return

    title = read_title(work_file)
    link = github_link(work_file)
    print(
        f"오늘 공부 주제: **{title}**\n"
        f"- 작업 파일: <{link}>\n"
        f"- `My Answer` 아래에 네 언어로 정리해줘\n"
        f"- 다 쓰면 말랑이 불러서 피드백 받으면 돼"
    )


if __name__ == "__main__":
    main()
