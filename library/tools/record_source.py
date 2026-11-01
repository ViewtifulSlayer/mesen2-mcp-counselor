#!/usr/bin/env python3
"""Record a source in a pack's local manifest, and optionally its public credit."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from _common import find_pack, read_json, rel, sha256_file, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True)
    parser.add_argument("--id", required=True, dest="source_id")
    parser.add_argument("--file", required=True, help="local file to hash")
    parser.add_argument("--path", help="path stored in the local manifest; defaults to the file path")
    parser.add_argument("--url")
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--redistribution", choices=["repo-safe", "local-only", "permissioned"], default="local-only")
    parser.add_argument("--region", default="US")
    parser.add_argument("--language", default="en")
    parser.add_argument("--covers", default="", help="comma-separated domains: overview,world,systems,data,harness,edgeCases,variants")
    parser.add_argument("--note")
    parser.add_argument("--permission-id")
    parser.add_argument("--public", action="store_true", help="also write the public credit entry")
    args = parser.parse_args()

    pack = find_pack(args.pack)
    source_file = Path(args.file).resolve()
    if not source_file.is_file():
        print(f"Source file not found: {source_file}", file=sys.stderr)
        return 2

    local_path = pack / "sources" / "manifest.local.json"
    local = read_json(local_path) if local_path.exists() else {"schemaVersion": 1, "sources": []}
    record = {
        "id": args.source_id,
        "path": args.path or rel(source_file),
        "sha256": sha256_file(source_file),
        "bytes": source_file.stat().st_size,
        "retrieved": date.today().isoformat(),
    }
    if args.url:
        record["url"] = args.url
    if args.note:
        record["notes"] = args.note
    local["sources"] = [source for source in local.get("sources", []) if source.get("id") != args.source_id]
    local["sources"].append(record)
    local["sources"].sort(key=lambda source: source["id"])
    write_json(local_path, local)
    print(f"Updated {local_path}")

    if args.public:
        public_path = pack / "sources" / "manifest.public.json"
        public = read_json(public_path) if public_path.exists() else {"schemaVersion": 1, "sources": []}
        entry = {
            "id": args.source_id,
            "title": args.title,
            "author": args.author,
            "license": args.license,
            "redistribution": args.redistribution,
            "covers": [item.strip() for item in args.covers.split(",") if item.strip()],
            "region": args.region,
            "language": args.language,
        }
        if args.note:
            entry["note"] = args.note
        if args.redistribution == "repo-safe" and args.url:
            entry["url"] = args.url
        if args.redistribution == "permissioned":
            if not args.permission_id:
                print("A permissioned public entry needs --permission-id", file=sys.stderr)
                return 2
            entry["permissionId"] = args.permission_id
        public["sources"] = [source for source in public.get("sources", []) if source.get("id") != args.source_id]
        public["sources"].append(entry)
        public["sources"].sort(key=lambda source: source["id"])
        write_json(public_path, public)
        print(f"Updated {public_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
