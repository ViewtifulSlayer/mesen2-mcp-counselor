#!/usr/bin/env python3
"""Validate Counselor packs.

Usage:
    python library/tools/validate_pack.py --all
    python library/tools/validate_pack.py --pack gb/final-fantasy-legend
    python library/tools/validate_pack.py --template
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _common import (
    PACKS_ROOT,
    REFERENCE_NAMES,
    SCHEMAS_ROOT,
    VARIANT_NAMES,
    citation_ids,
    error,
    find_pack,
    iter_packs,
    pack_forbidden,
    parse_frontmatter,
    read_json,
    rel,
    sha256_file,
    warning,
)

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - guidance for a bare environment
    print(
        "jsonschema is required. Run: python -m pip install -r library/tools/requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(2)


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "pack.json",
    "data/provenance.json",
    "sources/manifest.public.json",
    "sources/reading-plan.md",
    "tests/field-test.md",
    "CHANGELOG.md",
]
REQUIRED_REFERENCES = [f"references/{name}.md" for name in REFERENCE_NAMES]
REQUIRED_VARIANTS = [f"variants/{name}.md" for name in VARIANT_NAMES]


def load_schema(name: str) -> dict:
    return read_json(SCHEMAS_ROOT / name)


def schema_errors(data: dict, schema_name: str) -> list[str]:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        where = ".".join(str(part) for part in err.path) or "(root)"
        errors.append(f"{schema_name}: {where}: {err.message}")
    return errors


def check_manifest_privacy(source: dict) -> list[str]:
    problems = []
    if source.get("redistribution") == "local-only":
        for field in ("url", "path", "sha256", "bytes", "retrieved", "pages", "headings"):
            if field in source:
                problems.append(
                    f"source {source.get('id')}: local-only source must not include '{field}'"
                )
    if source.get("redistribution") == "permissioned" and not source.get("permissionId"):
        problems.append(f"source {source.get('id')}: permissioned source needs permissionId")
    return problems


def check_pack(pack: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    pack_json = pack / "pack.json"

    if not pack_json.exists():
        return [f"{rel(pack)}: missing pack.json"], warnings

    try:
        data = read_json(pack_json)
    except Exception as exc:
        return [f"{rel(pack_json)}: cannot read JSON: {exc}"], warnings

    errors.extend(schema_errors(data, "pack.schema.json"))

    for required in REQUIRED_FILES + REQUIRED_REFERENCES + REQUIRED_VARIANTS:
        if not (pack / required).exists():
            errors.append(f"{rel(pack)}: missing {required}")

    if data.get("id") != pack.name:
        errors.append(f"pack.json id '{data.get('id')}' does not match directory '{pack.name}'")

    skill_path = pack / "SKILL.md"
    if skill_path.exists():
        meta, _ = parse_frontmatter(skill_path)
        if not meta.get("name"):
            errors.append("SKILL.md: missing frontmatter name")
        if not meta.get("description"):
            errors.append("SKILL.md: missing frontmatter description")
        if data.get("skill", {}).get("name") != meta.get("name"):
            errors.append("SKILL.md frontmatter name does not match pack.json skill.name")

    for name in REFERENCE_NAMES:
        ref = pack / "references" / f"{name}.md"
        if not ref.exists():
            continue
        meta, _ = parse_frontmatter(ref)
        for field in ("title", "summary", "coverage"):
            if not meta.get(field):
                errors.append(f"{rel(ref)}: missing frontmatter {field}")
        if len(meta.get("summary", "")) > 160:
            errors.append(f"{rel(ref)}: summary is longer than 160 characters")
        if meta.get("coverage") not in {"none", "outline", "partial", "verified"}:
            errors.append(f"{rel(ref)}: invalid coverage '{meta.get('coverage')}'")

    public_path = pack / "sources" / "manifest.public.json"
    source_ids: set[str] = set()
    if public_path.exists():
        try:
            public = read_json(public_path)
        except Exception as exc:
            errors.append(f"{rel(public_path)}: cannot read JSON: {exc}")
            public = {}
        errors.extend(schema_errors(public, "source-public.schema.json"))
        for source in public.get("sources", []):
            sid = source.get("id")
            if sid in source_ids:
                errors.append(f"{rel(public_path)}: duplicate source id '{sid}'")
            source_ids.add(sid)
            errors.extend(check_manifest_privacy(source))

    reading_plan = pack / "sources" / "reading-plan.md"
    if reading_plan.exists():
        text = reading_plan.read_text(encoding="utf-8")
        if "http://" in text or "https://" in text:
            errors.append(
                f"{rel(reading_plan)}: public reading plans must not contain URLs; "
                "keep URLs in manifest.local.json"
            )

    for md in sorted(pack.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        for sid in citation_ids(text):
            if source_ids and sid not in source_ids:
                errors.append(f"{rel(md)}: citation [S:{sid}] is not in the public manifest")

    provenance_path = pack / "data" / "provenance.json"
    if provenance_path.exists():
        try:
            provenance = read_json(provenance_path)
        except Exception as exc:
            errors.append(f"{rel(provenance_path)}: cannot read JSON: {exc}")
            provenance = {}
        errors.extend(schema_errors(provenance, "provenance.schema.json"))
        records = {entry.get("file"): entry for entry in provenance.get("tables", [])}
        for data_file in data.get("data", []):
            path = pack / data_file
            if not path.exists():
                errors.append(f"{rel(pack)}: declared data file missing: {data_file}")
                continue
            record = records.get(data_file)
            if not record:
                errors.append(f"{rel(path)}: no provenance entry in data/provenance.json")
                continue
            actual = sha256_file(path)
            if record.get("sha256") != actual:
                errors.append(
                    f"{rel(path)}: provenance sha256 does not match the file "
                    f"(recorded {record.get('sha256')}, actual {actual})"
                )

    local_manifest = pack / "sources" / "manifest.local.json"
    if local_manifest.exists():
        from _common import is_git_ignored

        if not is_git_ignored(local_manifest):
            errors.append(
                f"{rel(local_manifest)}: local manifest exists but is not gitignored"
            )

    for path in sorted(pack.rglob("*")):
        if not path.is_file():
            continue
        if path.name in {".DS_Store", "Thumbs.db", "desktop.ini"}:
            errors.append(f"{rel(path)}: OS metadata file")
            continue
        reason = pack_forbidden(path, pack)
        if reason:
            errors.append(f"{rel(path)}: {reason}")

    status = data.get("status")
    if status in {"verified", "certified"}:
        field_test = pack / "tests" / "field-test.md"
        if field_test.exists() and len(field_test.read_text(encoding="utf-8").strip()) < 200:
            errors.append(f"{rel(field_test)}: a verified pack needs a real field-test procedure")
    if status == "certified":
        cert = pack / "CERTIFICATION.md"
        if not cert.exists():
            errors.append(f"{rel(pack)}: certified status requires CERTIFICATION.md")
        else:
            text = cert.read_text(encoding="utf-8")
            match = re.search(r"Score:\s*(\d+)\s*/\s*100", text)
            if not match:
                errors.append(f"{rel(cert)}: missing 'Score: NN/100'")
            elif int(match.group(1)) < 80:
                errors.append(f"{rel(cert)}: score below the 80/100 certification threshold")
            if "Rights failures: 0" not in text:
                errors.append(f"{rel(cert)}: certification must state 'Rights failures: 0'")

    if not data.get("data"):
        warnings.append(f"{rel(pack)}: no data tables declared")
    if not data.get("lua", {}).get("recipes"):
        warnings.append(f"{rel(pack)}: no Lua recipes declared")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="validate every pack")
    parser.add_argument("--pack", help="pack id or relative path")
    parser.add_argument("--template", action="store_true", help="validate the pack template")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    targets: list[Path] = []
    if args.all:
        targets.extend(iter_packs())
    if args.pack:
        targets.append(find_pack(args.pack))
    if args.template:
        targets.append(Path(__file__).resolve().parents[1] / "academy" / "templates" / "game-pack")

    if not targets:
        parser.print_help()
        return 2

    all_errors = 0
    for pack in targets:
        errors, warnings = check_pack(pack)
        print(f"\n{rel(pack)}")
        if errors:
            for message in errors:
                error(message)
        if warnings:
            for message in warnings:
                warning(message)
        if not errors:
            print("  OK")
        all_errors += len(errors)
        if args.strict:
            all_errors += len(warnings)

    print(f"\n{len(targets)} pack(s) checked; {all_errors} problem(s).")
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
