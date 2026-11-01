#!/usr/bin/env python3
"""Verify that local source files still match their recorded hashes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import REPO_ROOT, find_pack, iter_packs, read_json, rel, sha256_file


def check_pack(pack: Path, root: Path) -> int:
    manifest = pack / "sources" / "manifest.local.json"
    if not manifest.exists():
        print(f"{rel(pack)}: no local manifest; nothing to check.")
        return 0
    data = read_json(manifest)
    failures = 0
    for source in data.get("sources", []):
        path = Path(source["path"])
        if not path.is_absolute():
            path = (root / path).resolve()
        if not path.exists():
            print(f"  MISSING {source['id']}: {path}")
            failures += 1
            continue
        actual = sha256_file(path)
        if actual != source.get("sha256"):
            print(f"  MISMATCH {source['id']}: {path}")
            print(f"    recorded {source.get('sha256')}")
            print(f"    actual   {actual}")
            failures += 1
        else:
            print(f"  ok {source['id']}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", help="pack id or relative path")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--root", default=str(REPO_ROOT), help="base for relative local paths")
    args = parser.parse_args()

    packs = []
    if args.all:
        packs = iter_packs()
    elif args.pack:
        packs = [find_pack(args.pack)]
    else:
        parser.print_help()
        return 2

    failures = sum(check_pack(pack, Path(args.root).resolve()) for pack in packs)
    print(f"\n{len(packs)} pack(s), {failures} failure(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
