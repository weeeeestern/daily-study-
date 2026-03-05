#!/usr/bin/env python3
from __future__ import annotations

import subprocess

from common import current_topic, get_paths, gotify_send, load_dotenv, load_state, load_topics, save_state, today_kst


def run_git(repo: str, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True)


def is_done(work_text: str) -> bool:
    return "STATUS: DONE" in work_text


def main() -> int:
    paths = get_paths()
    load_dotenv(paths["env"])

    try:
        topics = load_topics(paths["topics"])
        state = load_state(paths["state"])
        idx, topic = current_topic(topics, state)

        work_path = paths["work_dir"] / f"{topic['id']}.md"
        if not work_path.exists() or not is_done(work_path.read_text(encoding="utf-8")):
            return 0

        repo = str(paths["repo_home"])
        run_git(repo, "add", "-A")
        run_git(repo, "commit", "-m", f"docs: daily study note ({today_kst()}) {topic['id']}")
        run_git(repo, "push", "origin", "main")

        state["current_index"] = (idx + 1) % len(topics)
        save_state(paths["state"], state)
        return 0
    except subprocess.CalledProcessError as exc:
        try:
            gotify_send("StudyBot Error", f"push_if_done.py git step failed: {exc}", priority=9)
        except Exception:
            pass
        raise
    except Exception as exc:  # noqa: BLE001
        try:
            gotify_send("StudyBot Error", f"push_if_done.py failed: {exc}", priority=9)
        except Exception:
            pass
        raise


if __name__ == "__main__":
    raise SystemExit(main())
