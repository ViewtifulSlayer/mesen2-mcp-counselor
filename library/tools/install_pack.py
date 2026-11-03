#!/usr/bin/env python3
"""Install a pack as an agent skill.

The installer copies public content only. It deliberately skips
sources/manifest.local.json and any local corpus data.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from _common import find_pack, read_json


def ignore_local(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in {"manifest.local.json", "__pycache__", ".git", ".gitkeep"}
        or name.endswith(".pyc")
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True)
    parser.add_argument("--target", default=".agents/skills")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    pack = find_pack(args.pack)
    data = read_json(pack / "pack.json")
    skill_name = data["skill"]["name"]
    target_root = Path(args.target)
    if not target_root.is_absolute():
        target_root = (Path.cwd() / target_root).resolve()
    destination = target_root / skill_name

    if destination.exists():
        if not args.force:
            print(f"Destination exists: {destination} (use --force to replace)", file=sys.stderr)
            return 2
        shutil.rmtree(destination)

    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(pack, destination, ignore=ignore_local)

    print(f"Installed {data['title']} to {destination}")
    print(f"Skill: {skill_name}")
    lua = data.get("lua") or {}
    if lua.get("libDir"):
        lib_dir = (destination / lua["libDir"]).resolve()
        print(f"Lua library: {lib_dir}")
        print("Add this to the Mesen2 MCP server arguments:")
        print(f"  --mcp-lib-dir={lib_dir}")
    else:
        print("No Lua kit: this pack uses a harness instead.")
        print(f"Harness: {destination / 'references' / 'harness.md'}")
    print("Restart the client so the skill list reloads.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
