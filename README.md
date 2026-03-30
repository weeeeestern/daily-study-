# Daily Study

Linux vs Windows 비교 학습을 매일 한 주제씩 진행하는 자동화 레포입니다.

## 핵심 흐름

- 오전 9시 (Asia/Seoul)
  - 현재 주제를 선택
  - `notes/work/YYYY-MM-DD-<topic>.md` 생성
  - `public/today.html` 갱신
- 사용자가 `## My Answer` 아래에 자기 언어로 정리
- 말랑이가 답변을 읽고 피드백
- 사용자가 `STATUS: DONE`으로 바꾸면
- 밤 11시 (Asia/Seoul)
  - 자동 commit / push
  - 다음 주제로 이동
- `STATUS: DONE`이 아니면 같은 주제가 다음날 반복됨

## 디렉토리 구조

- `topics.yml`: 30개+ 학습 주제
- `state.json`: 현재 진행 상태
- `notes/work/`: 공부 중인 파일
- `notes/final/`: 완료본 복사본
- `public/today.html`: 오늘의 주제 요약 페이지
- `scripts/generate_daily.py`: 아침 생성 스크립트
- `scripts/push_if_done.py`: 밤 커밋/푸시 스크립트
- `scripts/install_cron.sh`: cron 등록 스크립트
- `logs/`: 실행 로그

## 요구 사항

- Python 3
- `PyYAML` 설치
- Git push 권한

설치 예:

```bash
python3 -m pip install --user pyyaml
```

## 수동 실행

```bash
python3 scripts/generate_daily.py
python3 scripts/push_if_done.py
```

## cron 등록

```bash
bash scripts/install_cron.sh
```

## 작성 규칙

work 파일 맨 위에 반드시 상태가 있습니다.

```md
STATUS: TODO
```

완료 시:

```md
STATUS: DONE
```

이 문자열이 있어야 밤 자동 커밋/푸시가 진행됩니다.

## 주의

- public repo면 학습 내용이 공개됩니다.
- 민감한 정보는 적지 않는 편이 안전합니다.
- 현재 구현은 `main` 브랜치 push 기준입니다.
