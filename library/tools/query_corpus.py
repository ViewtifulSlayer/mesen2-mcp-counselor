#!/usr/bin/env python3
"""Query the local corpus index.

Examples:
    python library/tools/query_corpus.py "town data" --game secret-of-the-stars
    python library/tools/query_corpus.py "bridge east" --game final-fantasy-legend --json
    python library/tools/query_corpus.py --source-id guide-levinmage
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

from _common import CORPUS_ROOT, PACKS_ROOT, read_json

CJK_RE = re.compile(r"[\u3000-\u30ff\u3400-\u9fff\uff00-\uffef]")


def index_path(corpus: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    candidate = corpus / ".index" / "index.sqlite"
    if candidate.exists():
        return candidate
    return (CORPUS_ROOT / ".index" / "index.sqlite").resolve()


def source_records(source_id: str) -> list[dict]:
    records = []
    for path in sorted(PACKS_ROOT.glob("*/*/sources/manifest.local.json")):
        try:
            data = read_json(path)
        except Exception:
            continue
        for source in data.get("sources", []):
            if source.get("id") == source_id:
                record = dict(source)
                record["_manifest"] = str(path)
                records.append(record)
    return records


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="search text")
    parser.add_argument("--corpus", default=str(CORPUS_ROOT))
    parser.add_argument("--index", help="explicit index.sqlite path")
    parser.add_argument("--game")
    parser.add_argument("--category")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--source-id", help="resolve a pack source ID from local manifests")
    args = parser.parse_args()

    if args.source_id:
        records = source_records(args.source_id)
        if not records:
            print(f"No local manifest entry for source ID: {args.source_id}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(records, indent=2, ensure_ascii=False))
        else:
            for record in records:
                print(f"{record.get('id')}: {record.get('path')}")
                if record.get("sha256"):
                    print(f"  sha256 {record['sha256']}")
                if record.get("notes"):
                    print(f"  {record['notes']}")
        return 0

    if not args.query:
        parser.print_help()
        return 2

    corpus = Path(args.corpus).resolve()
    db_path = index_path(corpus, args.index)
    if not db_path.exists():
        print(f"Index not found: {db_path}", file=sys.stderr)
        print(
            "Run: python library/tools/ingest_corpus.py --corpus <game folder> --game <id>",
            file=sys.stderr,
        )
        return 2

    conn = sqlite3.connect(db_path)
    table = "docs_fts"
    if CJK_RE.search(args.query):
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='docs_cjk'"
        ).fetchone()
        if exists:
            table = "docs_cjk"

    phrase = '"' + args.query.replace('"', '""') + '"'
    params: list[object] = [phrase]
    filters = []
    if args.game:
        filters.append("game = ?")
        params.append(args.game)
    if args.category:
        filters.append("category = ?")
        params.append(args.category)
    where = " AND ".join([f"{table} MATCH ?"] + filters)
    sql = (
        f"SELECT path, game, category, title, heading, "
        f"snippet({table}, 5, '[', ']', '...', 12) AS snippet, bm25({table}) AS score "
        f"FROM {table} WHERE {where} ORDER BY score LIMIT ?"
    )
    params.append(args.limit)
    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError as exc:
        print(f"Query failed: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    results = [
        {
            "path": row[0],
            "game": row[1],
            "category": row[2],
            "title": row[3],
            "heading": row[4],
            "snippet": row[5],
            "score": row[6],
        }
        for row in rows
    ]
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0
    if not results:
        print("No matches.")
        return 0
    for item in results:
        print(f"\n{item['title']}  [{item['category']}]  {item['path']}")
        if item["heading"] and item["heading"] != item["title"]:
            print(f"  {item['heading']}")
        print(f"  {item['snippet']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
