#!/usr/bin/env python3
"""Uvicorn wrapper that fixes Railway passing literal '$PORT' as --port."""

from __future__ import annotations

import os
import sys


def _fix_args(argv: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--port", "-p") and i + 1 < len(argv):
            port = argv[i + 1]
            if port in {"$PORT", "${PORT}"} or not str(port).isdigit():
                port = os.environ.get("PORT", "8000")
            out.extend([arg, str(port)])
            i += 2
            continue
        if arg.startswith("--port="):
            val = arg.split("=", 1)[1]
            if val in {"$PORT", "${PORT}"} or not val.isdigit():
                val = os.environ.get("PORT", "8000")
            out.append(f"--port={val}")
            i += 1
            continue
        out.append(arg)
        i += 1
    return out


def main() -> None:
    from uvicorn.main import main as uvicorn_main

    sys.argv = [sys.argv[0], *_fix_args(sys.argv[1:])]
    uvicorn_main()


if __name__ == "__main__":
    main()
