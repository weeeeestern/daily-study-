#!/usr/bin/env python3
import datetime as dt
import html
import json
import os
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    raise

BASE_DIR = Path(__file__).resolve().parent.parent
TOPICS_PATH = BASE_DIR / "topics.yml"
STATE_PATH = BASE_DIR / "state.json"
WORK_DIR = BASE_DIR / "notes" / "work"
PUBLIC_DIR = BASE_DIR / "public"
LOG_DIR = BASE_DIR / "logs"
TIMEZONE_OFFSET_HOURS = 9  # Asia/Seoul


def now_kst():
    return dt.datetime.utcnow() + dt.timedelta(hours=TIMEZONE_OFFSET_HOURS)


def today_kst_str():
    return now_kst().date().isoformat()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def load_topics():
    with TOPICS_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    topics = data.get("topics", [])
    if not topics:
        raise ValueError("topics.yml contains no topics")
    return topics


def load_state(topics):
    if not STATE_PATH.exists():
        state = {
            "current_index": 0,
            "current_topic_id": topics[0]["id"],
            "last_generated_date": None,
            "last_completed_date": None,
        }
        save_state(state)
        return state

    with STATE_PATH.open("r", encoding="utf-8") as f:
        state = json.load(f)

    if state.get("current_topic_id") is None:
        idx = int(state.get("current_index", 0)) % len(topics)
        state["current_index"] = idx
        state["current_topic_id"] = topics[idx]["id"]
        save_state(state)
    return state


def save_state(state):
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def find_current_topic(topics, state):
    current_id = state.get("current_topic_id")
    for idx, topic in enumerate(topics):
        if topic["id"] == current_id:
            state["current_index"] = idx
            return topic
    idx = int(state.get("current_index", 0)) % len(topics)
    topic = topics[idx]
    state["current_index"] = idx
    state["current_topic_id"] = topic["id"]
    return topic


def build_work_filename(topic, date_str):
    return WORK_DIR / f"{date_str}-{slugify(topic['id'])}.md"


def concept_explanation(topic):
    return f"""### 주제 개요\n{topic['summary']}\n\n### Linux 관점 자세히\n{topic['linux_focus']}\n\n이 부분에서는 Linux/Unix 계열의 설계 철학, 실제 운영 방식, 그리고 명령줄·관리 도구와의 연결까지 생각해보면 좋다. 단순히 기능 차이를 외우기보다, 왜 이런 구조가 자연스럽게 자리잡았는지까지 설명할 수 있어야 한다.\n\n### Windows 관점 자세히\n{topic['windows_focus']}\n\n이 부분에서는 Windows NT 계열의 설계, GUI 중심 사용자 경험, 엔터프라이즈 관리 방식, 그리고 Microsoft 생태계와의 결합이 어떤 영향을 주는지 함께 보면 좋다.\n\n### 비교 포인트\n- 두 운영체제가 같은 문제를 어떻게 다르게 푸는가\n- 설계 차이가 실제 관리자 경험에 어떤 차이를 만드는가\n- 보안, 유지보수, 자동화 관점에서 어떤 장단점이 있는가\n\n### 왜 중요한가\n이 주제는 단순 기능 비교가 아니라, 운영체제의 철학과 관리 방식 차이를 이해하는 핵심 축이다. 이걸 이해하면 파일 시스템, 프로세스, 서비스, 보안, 업데이트 같은 후속 주제도 더 잘 연결된다."""


def build_work_content(topic, date_str):
    questions = [
        f"{topic['title']} 주제를 자기 언어로 설명해보세요.",
        "Linux와 Windows가 이 문제를 다르게 푸는 이유를 설계 관점에서 비교해보세요.",
        "이 차이가 실제 사용, 관리, 성능, 보안, 운영 경험에 어떤 영향을 주는지 설명해보세요.",
        "처음 배우는 사람에게 이 주제를 설명한다면 어떤 흐름으로 설명할지 적어보세요.",
    ]

    reading_links = "\n".join(f"- {link}" for link in topic.get("reading_links", []))

    return f"""STATUS: TODO\nDATE: {date_str}\nTOPIC_ID: {topic['id']}\n\n# {topic['title']}\n\n## 오늘의 목표\n이 주제를 읽고, Linux와 Windows의 차이를 단순 암기가 아니라 자기 언어로 설명할 수 있어야 한다.\n\n## 핵심 개념 설명\n{concept_explanation(topic)}\n\n## 꼭 알아야 할 것\n- 이 주제의 핵심 개념을 정의할 수 있어야 함\n- Linux 쪽 구현/철학을 설명할 수 있어야 함\n- Windows 쪽 구현/철학을 설명할 수 있어야 함\n- 두 시스템의 차이가 왜 생겼는지 추론할 수 있어야 함\n- 실무적으로 어떤 차이를 만드는지 연결해서 말할 수 있어야 함\n\n## 오늘의 질문\n1. {questions[0]}\n2. {questions[1]}\n3. {questions[2]}\n4. {questions[3]}\n\n## 실습 또는 관찰 포인트\n{topic['practice']}\n\n## 참고 자료\n{reading_links if reading_links else '- 없음'}\n\n## My Answer\n\n\n## Review\n- 말랑이 피드백 대기\n\n## Final Notes\n\n"""


def build_today_html(topic, date_str, work_file):
    links = "".join(
        f'<li><a href="{html.escape(link)}">{html.escape(link)}</a></li>'
        for link in topic.get("reading_links", [])
    )
    return f"""<!doctype html>
<html lang=\"ko\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Daily Study - {html.escape(topic['title'])}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 2rem auto; max-width: 900px; line-height: 1.7; padding: 0 1rem; background: #0f172a; color: #e2e8f0; }}
    h1, h2, h3 {{ color: #f8fafc; }}
    .card {{ background: #111827; border: 1px solid #334155; border-radius: 12px; padding: 1rem 1.25rem; margin: 1rem 0; }}
    code {{ background: #1e293b; padding: 0.1rem 0.35rem; border-radius: 6px; }}
    a {{ color: #93c5fd; }}
  </style>
</head>
<body>
  <h1>{html.escape(topic['title'])}</h1>
  <p><strong>Date:</strong> {html.escape(date_str)}</p>
  <div class=\"card\">
    <h2>Summary</h2>
    <p>{html.escape(topic['summary'])}</p>
  </div>
  <div class=\"card\">
    <h2>Linux Focus</h2>
    <p>{html.escape(topic['linux_focus'])}</p>
  </div>
  <div class=\"card\">
    <h2>Windows Focus</h2>
    <p>{html.escape(topic['windows_focus'])}</p>
  </div>
  <div class=\"card\">
    <h2>Practice</h2>
    <p>{html.escape(topic['practice'])}</p>
  </div>
  <div class=\"card\">
    <h2>Reading Links</h2>
    <ul>{links}</ul>
  </div>
  <div class=\"card\">
    <h2>Work File</h2>
    <p>{html.escape(work_file.name)}</p>
  </div>
</body>
</html>
"""


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    topics = load_topics()
    state = load_state(topics)
    topic = find_current_topic(topics, state)
    date_str = today_kst_str()
    work_file = build_work_filename(topic, date_str)

    if not work_file.exists():
        work_file.write_text(build_work_content(topic, date_str), encoding="utf-8")

    today_html = PUBLIC_DIR / "today.html"
    today_html.write_text(build_today_html(topic, date_str, work_file), encoding="utf-8")

    state["current_topic_id"] = topic["id"]
    state["last_generated_date"] = date_str
    save_state(state)

    message = (
        f"오늘 공부 주제 생성 완료\n"
        f"- date: {date_str}\n"
        f"- topic: {topic['title']}\n"
        f"- work_file: {work_file}\n"
        f"- today_html: {today_html}\n"
    )
    print(message)


if __name__ == "__main__":
    main()
