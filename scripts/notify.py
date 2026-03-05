#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import get_paths, gotify_send, load_dotenv


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a Gotify notification")
    parser.add_argument("title")
    parser.add_argument("message")
    parser.add_argument("--priority", type=int, default=5)
    args = parser.parse_args()

    paths = get_paths()
    load_dotenv(Path(paths["env"]))
    gotify_send(args.title, args.message, priority=args.priority)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
