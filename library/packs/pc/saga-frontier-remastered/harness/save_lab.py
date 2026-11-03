#!/usr/bin/env python3
"""Save-file lab for SaGa Frontier Remastered.

The on-disk save is a raw DEFLATE stream (RFC 1951) whose payload is JSON.
The inner slot state is a JSON string inside saveDataList[n].saveDataJsonStr.

This tool is deliberately small and stdlib-only:

    python save_lab.py inflate --input SaveData.bin --output SaveData.json
    python save_lab.py deflate --input SaveData.json --output test.bin
    python save_lab.py diff --left A.json --right B.json
    python save_lab.py assert-fixture --fixture asellus --input SaveData.bin.json

`deflate` is for test inputs. It is not byte-identical to the game's writer.
The integrity fields are not understood; this tool never edits a real save.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zlib
from pathlib import Path
from typing import Any


def payload_bytes(path: Path) -> tuple[bytes, str]:
    """Return (payload, kind) for a raw container or a JSON mirror."""
    raw = path.read_bytes()
    stripped = raw.lstrip()
    if stripped.startswith(b"{"):
        return raw, "json-mirror"
    try:
        return zlib.decompress(raw, -15), "raw-deflate"
    except zlib.error as exc:
        raise SystemExit(
            f"{path}: not raw DEFLATE and not JSON ({exc}). "
            "Raw DEFLATE needs wbits=-15, not zlib or gzip headers."
        ) from exc


def load_document(path: Path) -> dict[str, Any]:
    payload, _kind = payload_bytes(path)
    try:
        document = json.loads(payload.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"{path}: payload is not UTF-8 JSON ({exc})") from exc
    if not isinstance(document, dict):
        raise SystemExit(f"{path}: root JSON is not an object")
    return document


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def flatten(value: Any, prefix: str = "", parse_inner: bool = True, out: dict[str, Any] | None = None) -> dict[str, Any]:
    """Flatten nested JSON into dotted paths. Optionally parse JSON strings."""
    if out is None:
        out = {}
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            flatten(item, child, parse_inner, out)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            flatten(item, f"{prefix}[{index}]", parse_inner, out)
    elif isinstance(value, str) and parse_inner and value.lstrip().startswith("{"):
        try:
            inner = json.loads(value)
        except json.JSONDecodeError:
            out[prefix] = value
        else:
            flatten(inner, prefix, parse_inner, out)
    else:
        out[prefix] = value
    return out


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_bytes(path: Path, data: bytes, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"{path}: exists (pass --force to replace)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def command_inflate(args: argparse.Namespace) -> int:
    source = Path(args.input)
    payload, kind = payload_bytes(source)
    output = Path(args.output) if args.output else source.with_suffix(".json")
    write_bytes(output, payload, args.force)
    print(f"kind: {kind}")
    print(f"disk bytes: {source.stat().st_size}")
    print(f"payload bytes: {len(payload)}")
    print(f"payload sha256: {sha256(payload)}")
    print(f"wrote: {output}")
    return 0


def command_deflate(args: argparse.Namespace) -> int:
    source = Path(args.input)
    raw = source.read_bytes()
    try:
        json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"{source}: not UTF-8 JSON ({exc})") from exc
    compressor = zlib.compressobj(level=args.level, wbits=-15)
    packed = compressor.compress(raw) + compressor.flush()
    output = Path(args.output) if args.output else source.with_suffix(".bin")
    write_bytes(output, packed, args.force)
    print("kind: raw-deflate (test input)")
    print(f"payload bytes: {len(raw)}")
    print(f"container bytes: {len(packed)}")
    print(f"container sha256: {sha256(packed)}")
    print(f"wrote: {output}")
    print("warning: not byte-identical to the game's chunked writer; not a validity proof.")
    return 0


def ignored(key: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if key == pattern or key.startswith(pattern) or key.endswith(pattern):
            return True
    return False


def command_diff(args: argparse.Namespace) -> int:
    left = flatten(load_document(Path(args.left)), parse_inner=not args.no_parse_inner)
    right = flatten(load_document(Path(args.right)), parse_inner=not args.no_parse_inner)
    added = sorted(key for key in right if key not in left and not ignored(key, args.ignore))
    removed = sorted(key for key in left if key not in right and not ignored(key, args.ignore))
    changed = sorted(
        key
        for key in left
        if key in right and left[key] != right[key] and not ignored(key, args.ignore)
    )
    print(f"added: {len(added)}")
    print(f"removed: {len(removed)}")
    print(f"changed: {len(changed)}")
    shown = 0
    for label, keys in (("+", added), ("-", removed), ("~", changed)):
        for key in keys:
            if shown >= args.limit:
                print(f"... {len(added) + len(removed) + len(changed) - shown} more")
                return 0
            if label == "~":
                print(f"~ {key}: {left[key]!r} -> {right[key]!r}")
            elif label == "+":
                print(f"+ {key}: {right[key]!r}")
            else:
                print(f"- {key}: {left[key]!r}")
            shown += 1
    return 0


def check(results: list[tuple[str, bool, str]], label: str, actual: Any, expected: Any) -> None:
    ok = actual == expected
    detail = f"{actual!r} == {expected!r}" if ok else f"{actual!r} != {expected!r}"
    results.append((label, ok, detail))


def command_assert(args: argparse.Namespace) -> int:
    document = load_document(Path(args.input))
    results: list[tuple[str, bool, str]] = []

    if args.fixture == "asellus":
        slots = document.get("saveDataList") or []
        check(results, "saveDataList length", len(slots), 59)
        slot0 = slots[0]
        info = slot0["saveItemInfoData"]
        inner = json.loads(slot0["saveDataJsonStr"])
        quick = json.loads(document["quickSaveData"]["saveDataJsonStr"])
        auto = json.loads(document["autoSaveData"]["saveDataJsonStr"])
        check(results, "slot0 leader", info["CharacterNumber"], 5)
        check(results, "slot0 area", info["MapNumber"], 26)
        check(results, "slot0 hours", info["PlayTimeHours"], 0)
        check(results, "slot0 minutes", info["PlayTimeMinutes"], 11)
        check(results, "slot0 takeover", info.get("IsTakeover"), False)
        check(results, "slot0 money", inner["pty"]["money"], 100)
        check(results, "slot0 party count", inner["pty"]["psnCnt"], 1)
        check(results, "slot0 leader id", inner["pty"]["heroNo"], 5)
        check(results, "slot0 first item", inner["pty"]["item_a"][0], {"itemNo": 7, "itemCnt": 1})
        check(results, "slot0 current room", inner["mapwk"]["imfName"], "imf303")
        check(results, "slot0 area index", inner["mapwk"]["map_name"], 26)
        check(results, "slot0 previous map", inner["eventwk"]["mapNo"], 425)
        check(results, "slot0 chart 157 set", inner["pty"]["scenarioChartStateArray"][157] != 0, True)
        check(results, "slot0 chart 158 set", inner["pty"]["scenarioChartStateArray"][158] != 0, True)
        check(results, "slot0 battle rank points", inner["pty"]["each"]["parLev"], 0)
        check(results, "quick room", quick["mapwk"]["imfName"], "imf1a9")
        check(results, "quick previous map", quick["eventwk"]["mapNo"], 132)
        check(results, "auto room", auto["mapwk"]["imfName"], "imf303")
        check(results, "auto previous map", auto["eventwk"]["mapNo"], 425)
    else:
        slots = document.get("saveDataList") or []
        check(results, "saveDataList length", len(slots), 59)
        populated: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
        for index, entry in enumerate(slots):
            blob = entry.get("saveDataJsonStr")
            if not blob:
                continue
            populated.append((f"slot{index}", entry["saveItemInfoData"], json.loads(blob)))
        for label, entry in (("quick", document["quickSaveData"]), ("auto", document["autoSaveData"])):
            blob = entry.get("saveDataJsonStr")
            if blob:
                populated.append((label, entry["saveItemInfoData"], json.loads(blob)))
        check(results, "populated snapshots", len(populated), 5)
        allowed_rooms = {"imf00c", "imf00d", "imf055", "imf0dd"}
        for prefix, info, inner in populated:
            check(results, f"{prefix} leader", info["CharacterNumber"], 6)
            check(results, f"{prefix} area", info["MapNumber"], 3)
            check(results, f"{prefix} area index", inner["mapwk"]["map_name"], 3)
            check(results, f"{prefix} room in fixture set", inner["mapwk"]["imfName"] in allowed_rooms, True)
            check(results, f"{prefix} battle rank points", inner["pty"]["each"]["parLev"], 23)
            check(results, f"{prefix} party count", inner["pty"]["psnCnt"] in {2, 4}, True)
        slot1 = json.loads(slots[1]["saveDataJsonStr"])
        check(results, "slot1 room", slot1["mapwk"]["imfName"], "imf055")

    failures = [item for item in results if not item[1]]
    for label, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} {label}: {detail}")
    print(f"{len(results) - len(failures)}/{len(results)} checks passed")
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    inflate = sub.add_parser("inflate", help="raw DEFLATE to JSON")
    inflate.add_argument("--input", required=True)
    inflate.add_argument("--output")
    inflate.add_argument("--force", action="store_true")
    inflate.set_defaults(func=command_inflate)

    deflate = sub.add_parser("deflate", help="JSON to a raw DEFLATE test file")
    deflate.add_argument("--input", required=True)
    deflate.add_argument("--output")
    deflate.add_argument("--level", type=int, default=9, choices=range(0, 10))
    deflate.add_argument("--force", action="store_true")
    deflate.set_defaults(func=command_deflate)

    diff = sub.add_parser("diff", help="flatten two saves and report changed leaves")
    diff.add_argument("--left", required=True)
    diff.add_argument("--right", required=True)
    diff.add_argument("--limit", type=int, default=200)
    diff.add_argument("--no-parse-inner", action="store_true", help="do not parse saveDataJsonStr")
    diff.add_argument("--ignore", action="append", default=[], help="path prefix or suffix to ignore")
    diff.set_defaults(func=command_diff)

    assert_fixture = sub.add_parser("assert-fixture", help="check the Asellus or T260G contract")
    assert_fixture.add_argument("--fixture", required=True, choices=["asellus", "t260g"])
    assert_fixture.add_argument("--input", required=True)
    assert_fixture.set_defaults(func=command_assert)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
