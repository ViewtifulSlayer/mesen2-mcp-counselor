#!/usr/bin/env python3
"""Build deterministic Counselor Library release bundles.

Only files known to git (tracked or untracked-but-not-ignored) are considered.
The local corpus and local manifests can therefore never enter a bundle.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from _common import REPO_ROOT, read_json, rel

LIBRARY = REPO_ROOT / "library"
RELEASE_FILE = LIBRARY / "release.json"
VERSION_FILE = LIBRARY / "VERSION"
FORBIDDEN_EXT = {".smc", ".sfc", ".gb", ".gbc", ".gba", ".nes", ".mss", ".sav", ".srm", ".ips", ".bps", ".zip", ".rar", ".7z"}
FORBIDDEN_PARTS = {"example_library", "manifest.local.json", ".index"}


def version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def source_commit() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def tracked_or_untracked() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
            check=True,
            capture_output=True,
            text=True,
        )
        return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})
    except Exception:
        paths = []
        for path in REPO_ROOT.rglob("*"):
            if not path.is_file():
                continue
            relative = rel(path)
            if any(part in {".git", "dist", "example_library"} for part in path.parts):
                continue
            if relative.startswith("library/corpus/") and relative != "library/corpus/README.md":
                continue
            paths.append(relative)
        return sorted(paths)


def match(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def is_corpus_content(path: str) -> bool:
    if not path.startswith("library/corpus/"):
        return False
    return path != "library/corpus/README.md"


def eligible(path: str, spec: dict) -> bool:
    if is_corpus_content(path):
        return False
    if any(part in FORBIDDEN_PARTS for part in Path(path).parts):
        return False
    if Path(path).suffix.lower() in FORBIDDEN_EXT:
        return False
    if not match(path, spec.get("include", [])):
        return False
    if spec.get("exclude") and match(path, spec["exclude"]):
        return False
    return True


def zip_info(name: str, data: bytes, executable: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o755 if executable else 0o644) << 16
    return info


def bundle_info(name: str, version_value: str, files: list[str]) -> str:
    return (
        "Counselor Library bundle\n"
        f"Bundle: {name}\n"
        f"Version: {version_value}\n"
        f"Source commit: {source_commit()}\n"
        f"Files: {len(files)}\n"
        "Built from git-known files only; no corpus, ROMs, saves, or local manifests.\n"
        "License: content CC BY-SA 4.0; code GPL-3.0. See library/LICENSING.md.\n"
    )


def write_bundle(zip_path: Path, name: str, version_value: str, files: list[str], spec: dict) -> None:
    pack_prefix = None
    if name.startswith("pack:"):
        pack_id = name.split(":", 1)[1]
        pack_prefix = next(
            (
                path.rsplit("/", 1)[0]
                for path in files
                if path.endswith(f"/{pack_id}/pack.json")
            ),
            None,
        )

    entries: dict[str, bytes] = {}
    for path in files:
        source = REPO_ROOT / path
        if not source.is_file():
            continue
        archive_name = path
        if pack_prefix and path.startswith(pack_prefix + "/"):
            archive_name = path[len(pack_prefix) + 1 :]
        entries[archive_name] = source.read_bytes()

    entries["BUNDLE_INFO.txt"] = bundle_info(name, version_value, files).encode("utf-8")
    install = LIBRARY / "INSTALL.md"
    if install.exists():
        entries.setdefault("INSTALL.md", install.read_bytes())

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for archive_name in sorted(entries):
            archive.writestr(zip_info(archive_name, entries[archive_name]), entries[archive_name])


def inspect_bundle(zip_path: Path) -> list[str]:
    problems = []
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        if "BUNDLE_INFO.txt" not in names:
            problems.append(f"{zip_path.name}: missing BUNDLE_INFO.txt")
        for name in names:
            if any(part in FORBIDDEN_PARTS for part in Path(name).parts):
                problems.append(f"{zip_path.name}: forbidden path {name}")
            if Path(name).suffix.lower() in FORBIDDEN_EXT:
                problems.append(f"{zip_path.name}: forbidden extension {name}")
            if name.startswith("library/corpus/") and name != "library/corpus/README.md":
                problems.append(f"{zip_path.name}: corpus content {name}")
        if zip_path.name.startswith("counselor-pack-") and "SKILL.md" not in names:
            problems.append(f"{zip_path.name}: pack bundle has no root SKILL.md")
        if zip_path.name.startswith("counselor-library-") and not any(
            name.startswith("library/packs/") for name in names
        ):
            problems.append(f"{zip_path.name}: library bundle has no packs")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=version())
    parser.add_argument("--out", default=str(REPO_ROOT / "dist"))
    parser.add_argument("--bundle", default="all", help="all or a bundle name")
    parser.add_argument("--check", nargs="?", const="__build__", help="inspect bundles instead of building")
    args = parser.parse_args()

    if args.version != version():
        print(f"Version mismatch: tag/--version {args.version} != library/VERSION {version()}", file=sys.stderr)
        return 2

    release = read_json(RELEASE_FILE)
    all_files = tracked_or_untracked()

    if args.check:
        if args.check == "__build__":
            with tempfile.TemporaryDirectory() as temp:
                out = Path(temp)
                for name, spec in release["bundles"].items():
                    files = [path for path in all_files if eligible(path, spec)]
                    write_bundle(out / f"{name.replace(':', '-')}.zip", name, args.version, files, spec)
                problems = []
                for zip_path in sorted(out.glob("*.zip")):
                    problems.extend(inspect_bundle(zip_path))
        else:
            folder = Path(args.check).resolve()
            problems = []
            for zip_path in sorted(folder.glob("*.zip")):
                problems.extend(inspect_bundle(zip_path))
            if not list(folder.glob("*.zip")):
                problems.append(f"no bundles found in {folder}")
        if problems:
            for problem in problems:
                print(f"ERROR: {problem}", file=sys.stderr)
            return 1
        print("Bundle check passed.")
        return 0

    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    names = list(release["bundles"]) if args.bundle == "all" else [args.bundle]
    built = []
    for name in names:
        if name not in release["bundles"]:
            print(f"Unknown bundle: {name}", file=sys.stderr)
            return 2
        spec = release["bundles"][name]
        files = [path for path in all_files if eligible(path, spec)]
        if not files:
            print(f"Bundle {name} is empty", file=sys.stderr)
            return 2
        if name.startswith("pack:"):
            pack_id = name.split(":", 1)[1]
            pack = next((REPO_ROOT / p for p in files if p.endswith(f"/{pack_id}/pack.json")), None)
            if pack is None:
                print(f"Pack manifest not found for {name}", file=sys.stderr)
                return 2
            pack_version = read_json(pack)["packVersion"]
            zip_name = f"counselor-pack-{pack_id}-v{pack_version}.zip"
        else:
            zip_name = f"counselor-{name}-v{args.version}.zip"
        zip_path = out / zip_name
        write_bundle(zip_path, name, args.version, files, spec)
        built.append(zip_path)
        print(f"Wrote {zip_path} ({len(files)} files)")

    sums = out / "SHA256SUMS.txt"
    lines = []
    for zip_path in sorted(built):
        digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {zip_path.name}")
    sums.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {sums}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
