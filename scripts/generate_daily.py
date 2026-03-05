#!/usr/bin/env python3
from __future__ import annotations

import html
from pathlib import Path

from common import current_topic, get_paths, gotify_send, load_dotenv, load_state, load_topics


WORK_TEMPLATE = """STATUS: TODO

# {title}

## Today’s Goal

## Concept Summary

## Linux Focus

## Windows Focus

## Practice

## My Notes
"""


def render_today_html(topic: dict, work_path: Path) -> str:
    links = "".join(
        f'<li><a href="{html.escape(link)}" target="_blank" rel="noreferrer">{html.escape(link)}</a></li>'
        for link in topic["reading_links"]
    )
    return f"""<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <title>오늘의 공부 주제 - {html.escape(topic['title'])}</title>
</head>
<body>
  <h1>{html.escape(topic['title'])}</h1>
  <p><strong>Summary:</strong> {html.escape(topic['summary'])}</p>
  <p><strong>Linux Focus:</strong> {html.escape(topic['linux_focus'])}</p>
  <p><strong>Windows Focus:</strong> {html.escape(topic['windows_focus'])}</p>
  <p><strong>Practice:</strong> {html.escape(topic['practice'])}</p>
  <h2>Reading Links</h2>
  <ul>{links}</ul>
  <p>작업 파일: <code>{html.escape(str(work_path))}</code></p>
</body>
</html>
"""


def main() -> int:
    paths = get_paths()
    load_dotenv(paths["env"])

    try:
        topics = load_topics(paths["topics"])
        state = load_state(paths["state"])
        _, topic = current_topic(topics, state)

        work_dir = paths["work_dir"]
        work_dir.mkdir(parents=True, exist_ok=True)
        work_path = work_dir / f"{topic['id']}.md"
        if not work_path.exists():
            work_path.write_text(WORK_TEMPLATE.format(title=topic["title"]), encoding="utf-8")

        today_html = paths["today_html"]
        today_html.parent.mkdir(parents=True, exist_ok=True)
        today_html.write_text(render_today_html(topic, work_path), encoding="utf-8")

        import os
        today_link = os.environ.get("TODAY_URL", "http://172.30.1.81:8099/today.html")
        msg = f"{topic['summary']}\n\n링크: {today_link}"
        gotify_send(f"오늘 공부 알림: {topic['title']}", msg, priority=6)
        return 0
    except Exception as exc:  # noqa: BLE001
        try:
            gotify_send("StudyBot Error", f"generate_daily.py failed: {exc}", priority=9)
        except Exception:
            pass
        raise


if __name__ == "__main__":
    raise SystemExit(main())
