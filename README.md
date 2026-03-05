# Daily Study Automation System

Persistent study workflow engine that repeats the same topic until `STATUS: DONE` is written in the topic work file.

## Repository Contents

- `scripts/generate_daily.py`: 09:00 daily generator + Gotify notifier.
- `scripts/push_if_done.py`: 23:00 gatekeeper for git commit/push + topic rotation.
- `scripts/notify.py`: manual Gotify notification helper.
- `scripts/common.py`: shared config/state/topic helpers.
- `studybot/topics.yml`: 30-topic Linux vs Windows structured curriculum.
- `studybot/state.json`: current topic state tracker (`current_index`).
- `studybot/.env.example`: required and optional env variables.
- `studybot/crontab.txt`: cron schedule with `Asia/Seoul` timezone.

## Deployment Layout (target)

```text
/opt/studybot/
  ├── .env
  ├── state.json
  ├── topics.yml
  ├── scripts/
  │     ├── common.py
  │     ├── generate_daily.py
  │     ├── push_if_done.py
  │     ├── notify.py
  ├── logs/
  │     ├── gen.log
  │     ├── push.log

/opt/repos/daily-study-/
  ├── notes/work/
  ├── public/
```

## Setup

1. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy files:
   ```bash
   sudo mkdir -p /opt/studybot/scripts /opt/studybot/logs
   sudo cp scripts/*.py /opt/studybot/scripts/
   sudo cp studybot/topics.yml /opt/studybot/topics.yml
   sudo cp studybot/state.json /opt/studybot/state.json
   sudo cp studybot/.env.example /opt/studybot/.env
   ```
3. Edit `/opt/studybot/.env` and set real `GOTIFY_TOKEN`.
4. Ensure repo exists at `/opt/repos/daily-study-` and branch is `main`.
5. Install cron:
   ```bash
   crontab studybot/crontab.txt
   ```

## Behavior Summary

### 09:00 (`generate_daily.py`)

- Reads `/opt/studybot/topics.yml` and `/opt/studybot/state.json`.
- Resolves current topic from `current_index`.
- Creates `notes/work/<topic_id>.md` if missing (template includes `STATUS: TODO`).
- Generates `public/today.html`.
- Sends Gotify message:
  - Title: `오늘 공부 알림: <topic title>`
  - Message: topic summary + `TODAY_URL` link (default `http://172.30.1.81:8099/today.html`).
- On failure, sends `StudyBot Error` notification.

### 23:00 (`push_if_done.py`)

- Reads current topic work file.
- If file does **not** contain `STATUS: DONE`:
  - exits with no commit, no push, no state change.
- If file **does** contain `STATUS: DONE`:
  - `git add -A`
  - `git commit -m "docs: daily study note (YYYY-MM-DD) <topic_id>"`
  - `git push origin main`
  - advances `state.json` to next topic index.

## Work File Template

```md
STATUS: TODO

# Topic Title

## Today’s Goal
## Concept Summary
## Linux Focus
## Windows Focus
## Practice
## My Notes
```

This enforces repeat-until-done progression.
