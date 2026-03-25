from __future__ import annotations

import re


ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def strip_ansi(value: str) -> str:
    return ANSI_ESCAPE_RE.sub("", value)


def clean_terminal_output(value: str) -> str:
    return strip_ansi(value).strip()
