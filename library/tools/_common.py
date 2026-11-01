"""Shared helpers for the Counselor Library tools.

Keep this module dependency-free so every tool can import it in a bare Python
environment.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIBRARY_ROOT = REPO_ROOT / "library"
PACKS_ROOT = LIBRARY_ROOT / "packs"
SCHEMAS_ROOT = LIBRARY_ROOT / "schemas"
CORPUS_ROOT = LIBRARY_ROOT / "corpus"

REFERENCE_NAMES = (
    "overview",
    "world",
    "systems",
    "data",
    "harness",
    "edge-cases",
)
VARIANT_NAMES = ("jp", "us", "differences")

FORBIDDEN_EXTENSIONS = {
    ".smc",
    ".sfc",
    ".gb",
    ".gbc",
    ".gba",
    ".nes",
    ".mss",
    ".sav",
    ".srm",
    ".ips",
    ".bps",
    ".zip",
    ".rar",
    ".7z",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
}

FORBIDDEN_DIR_PARTS = {
    "roms",
    "saves",
    "manuals",
    "gamefaqs",
    "corpus",
    ".index",
}

MAX_PACK_FILE_BYTES = 1_000_000


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def rel(path: Path, base: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    """Return (frontmatter, body) for a simple YAML frontmatter block.

    Only scalar ``key: value`` lines are supported. That is deliberate: the
    library should not need a YAML parser just to read a title and summary.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return {}, text
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        meta[key.strip()] = value
    body = "\n".join(lines[end + 1 :])
    return meta, body


def iter_packs() -> list[Path]:
    if not PACKS_ROOT.exists():
        return []
    return sorted(path.parent for path in PACKS_ROOT.glob("*/*/pack.json"))


def git_tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_git_ignored(path: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "check-ignore", "-q", str(path)],
        capture_output=True,
    )
    return result.returncode == 0


def match_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def pack_forbidden(path: Path, pack_root: Path) -> str | None:
    """Return a reason if a pack file is forbidden, else None."""
    try:
        rel_path = path.relative_to(pack_root)
    except ValueError:
        return "outside the pack root"
    parts = set(rel_path.parts)
    if parts & FORBIDDEN_DIR_PARTS:
        return f"forbidden directory: {sorted(parts & FORBIDDEN_DIR_PARTS)}"
    if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
        return f"forbidden extension: {path.suffix.lower()}"
    if path.is_file() and path.stat().st_size > MAX_PACK_FILE_BYTES:
        return f"file is larger than {MAX_PACK_FILE_BYTES} bytes"
    return None


def citation_ids(text: str) -> set[str]:
    import re

    found = set(re.findall(r"\[S:([a-z0-9]+(?:-[a-z0-9]+)*)", text))
    found.discard("id")  # the documentation placeholder, not a citation
    return found


def find_pack(value: str) -> Path:
    """Resolve a pack by relative path or by id."""
    candidate = (REPO_ROOT / value).resolve()
    if candidate.is_dir() and (candidate / "pack.json").exists():
        return candidate
    candidate = (PACKS_ROOT / value).resolve()
    if candidate.is_dir() and (candidate / "pack.json").exists():
        return candidate
    for pack in iter_packs():
        if pack.name == value:
            return pack
    raise SystemExit(f"Pack not found: {value}")


def error(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def warning(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


def csv_rows(path: Path) -> list[list[str]]:
    import csv

    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
        return list(csv.reader(handle))
