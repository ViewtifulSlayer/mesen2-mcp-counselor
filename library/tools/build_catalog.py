#!/usr/bin/env python3
"""Generate CATALOG.md, PAGE_INDEX.md, catalog.json, and ATTRIBUTIONS.md."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

from _common import (
    REFERENCE_NAMES,
    VARIANT_NAMES,
    iter_packs,
    parse_frontmatter,
    read_json,
    rel,
    write_json,
    write_text,
)

LIBRARY = Path(__file__).resolve().parents[1]
VERSION_FILE = LIBRARY / "VERSION"
CATALOG_JSON = LIBRARY / "catalog.json"
CATALOG_MD = LIBRARY / "CATALOG.md"
PAGE_INDEX_MD = LIBRARY / "PAGE_INDEX.md"
ATTRIBUTIONS_MD = LIBRARY / "ATTRIBUTIONS.md"

COVERAGE_LABELS = {
    "overview": "Overview",
    "world": "World",
    "systems": "Systems",
    "data": "Data",
    "harness": "Harness",
    "edgeCases": "Edge cases",
    "variants": "Variants",
}


def library_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def public_sources(pack: Path) -> list[dict]:
    path = pack / "sources" / "manifest.public.json"
    if not path.exists():
        return []
    return read_json(path).get("sources", [])


def page_sources(sources: list[dict], coverage_key: str) -> int:
    key = {"edge-cases": "edgeCases"}.get(coverage_key, coverage_key)
    count = 0
    for source in sources:
        covers = source.get("covers", [])
        if not covers or key in covers:
            count += 1
    return count


def collect() -> dict:
    packs = []
    for pack in iter_packs():
        data = read_json(pack / "pack.json")
        sources = public_sources(pack)
        pages = []
        for name in REFERENCE_NAMES:
            path = pack / "references" / f"{name}.md"
            if not path.exists():
                continue
            meta, _ = parse_frontmatter(path)
            pages.append(
                {
                    "name": name,
                    "path": rel(path, LIBRARY),
                    "title": meta.get("title", name),
                    "summary": meta.get("summary", ""),
                    "coverage": meta.get("coverage", "none"),
                    "sources": page_sources(sources, name),
                }
            )
        pages.append(
            {
                "name": "variants",
                "path": rel(pack / "variants" / "differences.md", LIBRARY),
                "title": "Regional differences",
                "summary": "What changes between the regional releases.",
                "coverage": data.get("coverage", {}).get("variants", "none"),
                "sources": page_sources(sources, "variants"),
            }
        )
        packs.append(
            {
                "id": data["id"],
                "title": data["title"],
                "platform": data["platform"],
                "region": data["region"],
                "packVersion": data["packVersion"],
                "status": data["status"],
                "path": rel(pack, LIBRARY),
                "skill": data["skill"]["name"],
                "coverage": data["coverage"],
                "pages": pages,
                "sources": {
                    "total": len(sources),
                    "localOnly": sum(1 for s in sources if s.get("redistribution") == "local-only"),
                    "repoSafe": sum(1 for s in sources if s.get("redistribution") == "repo-safe"),
                    "permissioned": sum(1 for s in sources if s.get("redistribution") == "permissioned"),
                },
                "sourceList": sources,
                "variants": [
                    name
                    for name in VARIANT_NAMES
                    if (pack / "variants" / f"{name}.md").exists()
                ],
            }
        )
    return {
        "libraryVersion": library_version(),
        "packs": packs,
    }


def coverage_summary(coverage: dict) -> str:
    verified = sum(1 for value in coverage.values() if value == "verified")
    total = len(coverage)
    return f"{verified}/{total} verified"


def make_catalog_md(catalog: dict) -> str:
    lines = [
        "# Pack Catalog",
        "",
        f"Library version: `{catalog['libraryVersion']}`",
        "",
        "| Pack | Platform | Status | Version | Coverage | Pages | Sources |",
        "|---|---|---|---|---|---|---|",
    ]
    for pack in catalog["packs"]:
        link = f"[{pack['title']}]({pack['path']}/README.md)"
        lines.append(
            f"| {link} | {pack['platform']} | {pack['status']} | {pack['packVersion']} | "
            f"{coverage_summary(pack['coverage'])} | {len(pack['pages'])} | {pack['sources']['total']} |"
        )
    lines.extend(
        [
            "",
            "`verified` means the claims are tagged and a field test exists. `certified`",
            "also requires a rubric score in `CERTIFICATION.md`. Coverage is declared per",
            "domain in each pack's `pack.json`.",
            "",
            "The catalog lists public pages only. Local source paths, URLs, hashes, and the",
            "corpus index never appear here.",
            "",
        ]
    )
    return "\n".join(lines)


def make_page_index_md(catalog: dict) -> str:
    lines = [
        "# Page Index",
        "",
        "Every public page in the library, with the question it answers and its declared",
        "coverage. The per-pack `sources/reading-plan.md` is the source-page index.",
        "",
        "| Pack | Page | Question it answers | Coverage | Sources |",
        "|---|---|---|---|---|",
    ]
    for pack in catalog["packs"]:
        for page in pack["pages"]:
            title = page["title"].replace("|", "\\|")
            summary = page["summary"].replace("|", "\\|")
            lines.append(
                f"| {pack['title']} | [{title}]({page['path']}) | {summary} | "
                f"{page['coverage']} | {page['sources']} |"
            )
    lines.append("")
    return "\n".join(lines)


def make_attributions_md(catalog: dict) -> str:
    lines = [
        "# Attributions",
        "",
        "Sources consulted by public packs. Local-only sources are credited by title,",
        "author, and license; their URLs, paths, and hashes stay in `manifest.local.json`.",
        "No third-party text is included.",
        "",
    ]
    for pack in catalog["packs"]:
        lines.append(f"## {pack['title']}")
        lines.append("")
        if not pack["sourceList"]:
            lines.append("No public source entries.")
            lines.append("")
            continue
        for source in pack["sourceList"]:
            status = source.get("redistribution", "local-only")
            lines.append(
                f"- **{source.get('title', 'Untitled')}** by {source.get('author', 'Unknown')} "
                f"({source.get('license', 'unknown')}; {status})."
            )
            if source.get("note"):
                lines.append(f"  - {source['note']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated files are stale")
    args = parser.parse_args()

    catalog = collect()
    generated = {
        CATALOG_JSON: json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        CATALOG_MD: make_catalog_md(catalog),
        PAGE_INDEX_MD: make_page_index_md(catalog),
        ATTRIBUTIONS_MD: make_attributions_md(catalog),
    }

    stale = []
    for path, content in generated.items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != content:
            stale.append(path)
            if not args.check:
                if path.suffix == ".json":
                    write_json(path, catalog)
                else:
                    write_text(path, content)

    if args.check:
        if stale:
            print("Stale generated files:", file=sys.stderr)
            for path in stale:
                print(f"  {rel(path)}", file=sys.stderr)
                current = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
                expected = generated[path].splitlines()
                diff = list(difflib.unified_diff(current, expected, lineterm="", n=1))
                for line in diff[:20]:
                    print(f"    {line}", file=sys.stderr)
            return 1
        print("Catalog, page index, and attributions are fresh.")
        return 0

    print(f"Wrote {len(generated)} generated files for {len(catalog['packs'])} pack(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
