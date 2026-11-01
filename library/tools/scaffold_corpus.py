#!/usr/bin/env python3
"""Create the local corpus scaffold.

The corpus is user-supplied and gitignored. This tool only creates the category
directories and, with --adopt, points at an existing folder so the 343 MB example
does not have to be duplicated.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from _common import CORPUS_ROOT, REPO_ROOT, now_utc, rel, write_text

CATEGORIES = {
    "guides": "Text and HTML walkthroughs, FAQs, and boss guides you already have.",
    "manuals": "Scanned manuals, PDFs, and page images.",
    "maps": "Screenshots, rendered maps, and tile maps.",
    "data": "CSV/JSON/spreadsheets, RAM notes, and technical documents.",
    "websites": "Mirrored sites and their assets.",
    "regional": "Japanese, European, or other regional sources.",
    "saves": "Savestates, SRM files, and battery saves.",
    "roms": "Your ROMs. They are hashed for identification and never indexed.",
    "patches": "IPS/BPS patches and patch documentation.",
    "notes": "Your own notes and observations.",
}

CATEGORY_README = """{title}

{description}

This directory is part of the local corpus. It is gitignored. Do not commit its
contents. The public repository does not distribute or link to copyrighted
guides, manuals, maps, ROMs, or saves.
"""

ADOPT_MAP = {
    "gamefaqs": "guides",
    "docs": "data",
    "manuals": "manuals",
    "maps": "maps",
    "roms": "roms",
    "saves": "saves",
    "websites": "websites",
    "patches": "patches",
    "notes": "notes",
}


def make_category(root: Path, name: str, description: str, force: bool) -> None:
    path = root / name
    path.mkdir(parents=True, exist_ok=True)
    readme = path / "README.txt"
    if not readme.exists() or force:
        write_text(readme, CATEGORY_README.format(title=name.title(), description=description))


def move_if_present(source: Path, target: Path, force: bool) -> bool:
    if not source.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if not force:
            print(f"  skip {source.name}: {target} already exists (use --force)")
            return False
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    shutil.move(str(source), str(target))
    print(f"  moved {source} -> {target}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(CORPUS_ROOT), help="corpus root")
    parser.add_argument("--platform", required=True, help="e.g. snes, gb")
    parser.add_argument("--game", required=True, help="game id, e.g. secret-of-the-stars")
    parser.add_argument("--adopt", help="existing game folder to point at or move")
    parser.add_argument("--move", action="store_true", help="move categories into the scaffold")
    parser.add_argument("--force", action="store_true", help="overwrite generated files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    game_root = root / args.platform / args.game
    game_root.mkdir(parents=True, exist_ok=True)

    for name, description in CATEGORIES.items():
        make_category(game_root, name, description, args.force)

    pointer = game_root / "corpus.json"
    if args.adopt:
        source = Path(args.adopt).resolve()
        if not source.is_dir():
            print(f"adopt source is not a directory: {source}", file=sys.stderr)
            return 2
        if args.move:
            print(f"Adopting and moving {source} into {game_root}")
            for existing, canonical in ADOPT_MAP.items():
                src = source / existing
                if not src.exists():
                    continue
                if existing == "websites":
                    jp = src / "Aqutallion JP Guide"
                    if jp.exists():
                        move_if_present(jp, game_root / "regional" / "jp" / "aqutallion-guide", args.force)
                    for child in list(src.iterdir()):
                        if child == jp:
                            continue
                        move_if_present(child, game_root / "websites" / child.name, args.force)
                    try:
                        src.rmdir()
                    except OSError:
                        pass
                else:
                    for child in list(src.iterdir()):
                        move_if_present(child, game_root / canonical / child.name, args.force)
                    try:
                        src.rmdir()
                    except OSError:
                        pass
        data = {
            "platform": args.platform,
            "game": args.game,
            "source_root": rel(source),
            "canonical_root": rel(game_root),
            "categories": list(CATEGORIES),
            "created": now_utc(),
            "notes": "Local pointer. Gitignored. Use --follow-pointer with ingest_corpus.py.",
        }
        pointer.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {pointer}")
    else:
        print(f"Created corpus scaffold at {game_root}")

    print("\nCategories:")
    for name in CATEGORIES:
        print(f"  {name}/")
    print("\nNext:")
    print(f"  python library/tools/ingest_corpus.py --corpus {game_root} --game {args.game}")
    print("Do not commit the corpus. It is gitignored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
