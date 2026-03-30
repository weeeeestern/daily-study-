#!/usr/bin/env python3
import datetime as dt
import json
import os
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = BASE_DIR / "state.json"
TOPICS_PATH = BASE_DIR / "topics.yml"
WORK_DIR = BASE_DIR / "notes" / "work"
FINAL_DIR = BASE_DIR / "notes" / "final"
TIMEZONE_OFFSET_HOURS = 9  # Asia/Seoul
SSH_COMMAND = "ssh -i ~/.ssh/id_ed25519_daily_study -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"


def now_kst():
    return dt.datetime.utcnow() + dt.timedelta(hours=TIMEZONE_OFFSET_HOURS)


def today_kst_str():
    return now_kst().date().isoformat()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_topics():
    import yaml
    with TOPICS_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["topics"]


def topic_by_id(topics, topic_id):
    for idx, topic in enumerate(topics):
        if topic["id"] == topic_id:
            return idx, topic
    raise ValueError(f"Topic not found: {topic_id}")


def find_latest_work_file(topic_id: str):
    pattern = f"*-{slugify(topic_id)}.md"
    matches = sorted(WORK_DIR.glob(pattern))
    return matches[-1] if matches else None


def status_is_done(work_file: Path):
    content = work_file.read_text(encoding="utf-8")
    return "STATUS: DONE" in content


def export_final_copy(work_file: Path):
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    final_path = FINAL_DIR / work_file.name
    final_path.write_text(work_file.read_text(encoding="utf-8"), encoding="utf-8")
    return final_path


def git(*args, env=None):
    return subprocess.run(["git", *args], cwd=BASE_DIR, check=True, capture_output=True, text=True, env=env)


def main():
    state = load_json(STATE_PATH)
    topics = load_topics()
    idx, topic = topic_by_id(topics, state["current_topic_id"])
    work_file = find_latest_work_file(topic["id"])

    if work_file is None:
        print(f"STUDY_STATUS: NO_WORK_FILE\n현재 주제 파일이 없어. topic={topic['id']}")
        return

    if not status_is_done(work_file):
        print(f"STUDY_STATUS: NOT_DONE\n아직 완료되지 않았어. topic={topic['id']}")
        return

    final_path = export_final_copy(work_file)
    commit_date = today_kst_str()
    git("add", "-A")
    git("commit", "-m", f"docs: daily study note ({commit_date}) {topic['id']}")

    push_env = dict(os.environ)
    push_env["GIT_SSH_COMMAND"] = SSH_COMMAND
    git("push", "origin", "main", env=push_env)

    next_idx = (idx + 1) % len(topics)
    state["current_index"] = next_idx
    state["current_topic_id"] = topics[next_idx]["id"]
    state["last_completed_date"] = commit_date
    save_json(STATE_PATH, state)

    print(
        f"STUDY_STATUS: PUSHED\n"
        f"오늘 공부 완료본을 푸시했어.\n"
        f"- topic: {topic['id']}\n"
        f"- work: {work_file.name}\n"
        f"- final: {final_path.name}\n"
        f"- next_topic: {topics[next_idx]['id']}"
    )


if __name__ == "__main__":
    main()
