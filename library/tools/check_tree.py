#!/usr/bin/env python3
"""Fail fast when a directory the library contract requires is missing.

Git does not store empty directories. A pack or template authored on a machine
where `lua/lib/recipes/` happens to exist looks fine locally and loses that
directory in a clean checkout, which is exactly how the 0.1.0 release run found
`test_rom_file_is_rejected` crashing on a missing `lua/lib`.

This check runs before validation so the failure names the directory instead of
surfacing later as a FileNotFoundError in a test or a bundle that quietly ships
one folder short. Empty directories that belong to the contract carry a
`.gitkeep` placeholder; the installer skips that file, so it never reaches an
installed skill or a pack.

Checks, for the pack template and every pack under `library/packs/`:

* each required or declared directory exists;
* it is not empty (a `.gitkeep` counts);
* when the tree is a git checkout, it has at least one tracked file, so it
  survives a clean clone.

Usage:

    python library/tools/check_tree.py
    python library/tools/check_tree.py --root path/to/checkout
    python library/tools/check_tree.py --no-git
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

TEMPLATE_DIR = Path("library/academy/templates/game-pack")
PACKS_DIR = Path("library/packs")

TEMPLATE_REQUIRED_DIRS = (
    "data",
    "references",
    "sources",
    "assets/schematics",
    "lua/lib/recipes",
    "tests",
    "variants",
)
TEMPLATE_REQUIRED_FILES = (
    "SKILL.md",
    "pack.json",
    "sources/manifest.public.json",
    "tests/field-test.md",
)


def tracked_files(root: Path) -> set[str] | None:
    """Return tracked paths under library/, or None when git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--", "library"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return {path for path in result.stdout.split("\0") if path}


def check_dir(root: Path, label: str, relative: str, tracked: set[str] | None) -> list[str]:
    path = root / relative
    if not path.is_dir():
        return [f"{label}: missing directory {relative}/"]
    problems: list[str] = []
    if not any(path.iterdir()):
        problems.append(
            f"{label}: empty directory {relative}/ (add content or a .gitkeep placeholder)"
        )
    elif tracked is not None and not any(
        entry == relative or entry.startswith(relative + "/") for entry in tracked
    ):
        problems.append(
            f"{label}: directory {relative}/ has no tracked files, so a clean "
            "checkout will not create it"
        )
    return problems


def check_file(root: Path, label: str, relative: str, tracked: set[str] | None) -> list[str]:
    if not (root / relative).is_file():
        return [f"{label}: missing file {relative}"]
    if tracked is not None and relative not in tracked:
        return [f"{label}: file {relative} is not tracked by git"]
    return []


def pack_requirements(pack_dir: Path, label: str) -> tuple[list[str], list[str]]:
    """Return the directories and files a pack declares in pack.json."""
    try:
        manifest = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise SystemExit(f"{label}: cannot read pack.json: {error}") from error

    directories: list[str] = []
    files: list[str] = ["pack.json"]

    skill = manifest.get("skill") or {}
    if skill.get("entry"):
        files.append(str(skill["entry"]))

    sources = manifest.get("sources") or {}
    if sources.get("public"):
        files.append(str(sources["public"]))

    files.extend(str(item) for item in manifest.get("data") or [])
    files.extend(str(item) for item in manifest.get("tests") or [])

    harness = manifest.get("harness") or {}
    files.extend(str(item) for item in harness.get("scripts") or [])

    lua = manifest.get("lua") or {}
    lib_dir = lua.get("libDir")
    if lib_dir:
        directories.append(str(lib_dir))
        for recipe in lua.get("recipes") or []:
            name = str(recipe)
            candidates = [
                f"{lib_dir}/recipes/{name}.lua",
                f"{lib_dir}/{name}.lua",
            ]
            files.append(next((c for c in candidates if (pack_dir / c).is_file()), candidates[0]))

    return directories, files


def check(root: Path, use_git: bool = True) -> list[str]:
    tracked = tracked_files(root) if use_git else None
    problems: list[str] = []

    template = root / TEMPLATE_DIR
    if not template.is_dir():
        return [f"pack template: missing directory {TEMPLATE_DIR.as_posix()}/"]

    for relative in TEMPLATE_REQUIRED_DIRS:
        problems += check_dir(root, "pack template", (TEMPLATE_DIR / relative).as_posix(), tracked)
    for relative in TEMPLATE_REQUIRED_FILES:
        problems += check_file(root, "pack template", (TEMPLATE_DIR / relative).as_posix(), tracked)

    pack_dirs = sorted(path.parent for path in (root / PACKS_DIR).glob("*/*/pack.json"))
    if not pack_dirs:
        problems.append(f"packs: no packs found under {PACKS_DIR.as_posix()}/")

    for pack_dir in pack_dirs:
        relative_pack = pack_dir.relative_to(root).as_posix()
        label = f"{relative_pack}"
        directories, files = pack_requirements(pack_dir, label)
        for relative in directories:
            problems += check_dir(root, label, f"{relative_pack}/{relative}", tracked)
        for relative in files:
            problems += check_file(root, label, f"{relative_pack}/{relative}", tracked)

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the library tree layout.")
    parser.add_argument("--root", default=None, help="Repository root (default: this checkout)")
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip the tracked-file checks, for source archives without a .git directory",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    problems = check(root, use_git=not args.no_git)

    if problems:
        print(f"Tree check failed with {len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    packs = len(list((root / PACKS_DIR).glob("*/*/pack.json")))
    mode = "git-tracked" if not args.no_git else "filesystem-only"
    print(f"Tree check passed ({mode}): template and {packs} pack(s) have every declared directory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
