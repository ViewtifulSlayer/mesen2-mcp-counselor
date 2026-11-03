"""Unit and integration tests for the Counselor Library tools.

Run from the repository root:

    python -m unittest discover -s library/tools/tests -v

The fixtures are original text. They exist to exercise decoding, indexing,
cataloguing, validation, installation, and bundling without any copyrighted
material.
"""

from __future__ import annotations

import copy
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
REPO = TOOLS.parents[1]
TEMPLATE = REPO / "library" / "academy" / "templates" / "game-pack"
FIXTURE_CORPUS = Path(__file__).resolve().parent / "fixtures" / "corpus"

sys.path.insert(0, str(TOOLS))

import build_bundles  # noqa: E402
from validate_pack import check_pack  # noqa: E402


def run(*args: str, cwd: Path = REPO) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def pack_manifests() -> list[Path]:
    return sorted((REPO / "library" / "packs").glob("*/*/pack.json"))


def authoring_pack_gaps(packs: list[Path], archive_names: set[str]) -> list[str]:
    required = {
        f"{manifest.parent.relative_to(REPO).as_posix()}/{name}"
        for manifest in packs
        for name in ("pack.json", "SKILL.md")
    }
    return sorted(required - archive_names)


class TemplateValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.pack = Path(self.temp.name) / "game-pack"
        shutil.copytree(TEMPLATE, self.pack)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def errors(self) -> list[str]:
        errors, _warnings = check_pack(self.pack)
        return errors

    def test_template_is_clean(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_unknown_citation_is_rejected(self) -> None:
        manifest = self.pack / "sources" / "manifest.public.json"
        manifest.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "sources": [
                        {
                            "id": "fixture-source",
                            "title": "Fixture source",
                            "author": "Fixture author",
                            "license": "CC0-1.0",
                            "redistribution": "repo-safe",
                            "covers": ["overview"],
                            "region": "US",
                            "language": "en",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        overview = self.pack / "references" / "overview.md"
        overview.write_text(
            overview.read_text(encoding="utf-8") + "\nSee [S:not-a-source].\n",
            encoding="utf-8",
        )
        self.assertTrue(any("not in the public manifest" in item for item in self.errors()))

    def test_local_only_url_is_rejected(self) -> None:
        manifest = self.pack / "sources" / "manifest.public.json"
        manifest.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "sources": [
                        {
                            "id": "fixture-source",
                            "title": "Fixture source",
                            "author": "Fixture author",
                            "license": "all-rights-reserved",
                            "redistribution": "local-only",
                            "covers": ["overview"],
                            "region": "US",
                            "language": "en",
                            "url": "https://example.invalid/guide",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        errors = self.errors()
        self.assertTrue(any("must not include 'url'" in item for item in errors))

    def test_provenance_hash_mismatch_is_rejected(self) -> None:
        table = self.pack / "data" / "sample.csv"
        table.write_text("id,value\n1,fixture\n", encoding="utf-8")
        pack_json = self.pack / "pack.json"
        data = json.loads(pack_json.read_text(encoding="utf-8"))
        data["data"] = ["data/sample.csv"]
        pack_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        provenance = self.pack / "data" / "provenance.json"
        provenance.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "tables": [
                        {
                            "file": "data/sample.csv",
                            "origin": "observation",
                            "source": "fixture",
                            "generator": "tests",
                            "sha256": "0" * 64,
                            "verifiedOn": "2026-11-01",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.assertTrue(
            any("provenance sha256 does not match" in item for item in self.errors())
        )

    def test_rom_file_is_rejected(self) -> None:
        rom = self.pack / "lua" / "lib" / "sample.gb"
        rom.parent.mkdir(parents=True, exist_ok=True)
        rom.write_bytes(b"not a rom")
        self.assertTrue(any("forbidden extension" in item for item in self.errors()))

    def test_save_file_is_rejected(self) -> None:
        save = self.pack / "data" / "SaveData.bin"
        save.write_bytes(b"not a save")
        self.assertTrue(any("forbidden extension" in item for item in self.errors()))


class TreeLayoutTest(unittest.TestCase):
    def stage(self, root: Path) -> None:
        """Stage the copied tree so the preflight sees tracked files."""
        subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)

    def test_repository_layout_is_complete(self) -> None:
        result = run(str(TOOLS / "check_tree.py"), "--no-git")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_template_directory_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(TEMPLATE, root / "library" / "academy" / "templates" / "game-pack")
            shutil.copytree(
                REPO / "library" / "packs" / "gb" / "final-fantasy-legend",
                root / "library" / "packs" / "gb" / "final-fantasy-legend",
            )
            shutil.rmtree(root / "library" / "academy" / "templates" / "game-pack" / "lua")

            result = run(str(TOOLS / "check_tree.py"), "--root", str(root), "--no-git")

            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("pack template: missing directory", result.stderr)
            self.assertIn("lua/lib/recipes", result.stderr)

    def test_placeholder_keeps_an_empty_directory_tracked(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            template = root / "library" / "academy" / "templates" / "game-pack"
            shutil.copytree(TEMPLATE, template)
            shutil.copytree(
                REPO / "library" / "packs" / "gb" / "final-fantasy-legend",
                root / "library" / "packs" / "gb" / "final-fantasy-legend",
            )
            self.stage(root)
            self.assertEqual(
                run(str(TOOLS / "check_tree.py"), "--root", str(root)).returncode,
                0,
            )

            # Drop the placeholder from the index. The directory still exists on
            # disk, but a clean checkout would not create it.
            subprocess.run(
                ["git", "rm", "-q", "--cached", "library/academy/templates/game-pack/assets/schematics/.gitkeep"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            result = run(str(TOOLS / "check_tree.py"), "--root", str(root))
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("has no tracked files", result.stderr)


class CorpusIngestTest(unittest.TestCase):
    def test_ingest_and_query(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            game_root = Path(temp) / "corpus" / "snes" / "test-game"
            shutil.copytree(FIXTURE_CORPUS / "snes" / "test-game", game_root)
            manuals = game_root / "manuals"
            manuals.mkdir()
            (manuals / "notes.pdf").write_text(
                "Fixture placeholder. Not a PDF and not a manual.\n", encoding="utf-8"
            )
            out = Path(temp) / "index"
            result = run(
                str(TOOLS / "ingest_corpus.py"),
                "--corpus",
                str(Path(temp) / "corpus"),
                "--game",
                "test-game",
                "--out",
                str(out),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            meta = json.loads((out / "catalog.json").read_text(encoding="utf-8"))
            files = meta["files"]
            self.assertEqual(meta["meta"]["files"], 4)
            self.assertEqual(meta["meta"]["indexedFiles"], 3)
            self.assertEqual(meta["meta"]["catalogOnly"], 1)
            self.assertEqual(
                {item["path"] for item in files if not item["indexed"]},
                {"manuals/notes.pdf"},
            )
            html = next(item for item in files if item["path"] == "websites/shrine.html")
            self.assertEqual(html["title"], "Shrine of the East")
            jp = next(item for item in files if item["path"] == "regional/jp/tower.txt")
            self.assertEqual(jp["lang"], "ja")

            hit = run(
                str(TOOLS / "query_corpus.py"),
                "airship",
                "--index",
                str(out / "index.sqlite"),
            )
            self.assertEqual(hit.returncode, 0, hit.stderr)
            self.assertIn("sample-guide.txt", hit.stdout)

            if meta["meta"]["cjkIndex"]:
                cjk = run(
                    str(TOOLS / "query_corpus.py"),
                    "北の塔",
                    "--index",
                    str(out / "index.sqlite"),
                )
                self.assertEqual(cjk.returncode, 0, cjk.stderr)
                self.assertIn("tower.txt", cjk.stdout)


class InstallAndBundleTest(unittest.TestCase):
    def test_install_pack_copies_public_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skills"
            result = run(
                str(TOOLS / "install_pack.py"),
                "--pack",
                "gb/final-fantasy-legend",
                "--target",
                str(target),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            skill = target / "ffl-gameplay"
            self.assertTrue((skill / "SKILL.md").exists())
            self.assertTrue((skill / "references" / "systems.md").exists())
            self.assertFalse((skill / "sources" / "manifest.local.json").exists())

    def test_bundles_are_reproducible_and_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "dist"
            built = run(str(TOOLS / "build_bundles.py"), "--out", str(out))
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            self.assertTrue((out / "SHA256SUMS.txt").exists())

            checked = run(str(TOOLS / "build_bundles.py"), "--check", str(out))
            self.assertEqual(checked.returncode, 0, checked.stderr)

            for archive in out.glob("*.zip"):
                with zipfile.ZipFile(archive) as zipped:
                    names = zipped.namelist()
                self.assertIn("BUNDLE_INFO.txt", names)
                self.assertFalse(
                    any(name.startswith("library/corpus/") and name != "library/corpus/README.md" for name in names),
                    f"{archive.name} contains corpus content",
                )
                self.assertFalse(
                    any(name.endswith("manifest.local.json") for name in names),
                    f"{archive.name} contains a local manifest",
                )

    def test_authoring_bundle_contains_every_pack(self) -> None:
        packs = pack_manifests()
        self.assertTrue(packs, "No pack manifests found under library/packs")

        version = (REPO / "library" / "VERSION").read_text(encoding="utf-8").strip()

        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "dist"
            built = run(
                str(TOOLS / "build_bundles.py"),
                "--bundle",
                "authoring",
                "--out",
                str(out),
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)

            archive = out / f"counselor-authoring-v{version}.zip"
            self.assertTrue(archive.exists(), f"missing authoring archive: {archive}")
            with zipfile.ZipFile(archive) as zipped:
                names = set(zipped.namelist())

        missing = authoring_pack_gaps(packs, names)
        self.assertEqual(
            missing,
            [],
            f"Authoring bundle is missing pack file(s): {', '.join(missing)}",
        )

    def test_authoring_guard_detects_a_removed_pack_include(self) -> None:
        packs = pack_manifests()
        self.assertTrue(packs, "No pack manifests found under library/packs")
        release = json.loads(
            (REPO / "library" / "release.json").read_text(encoding="utf-8")
        )
        spec = copy.deepcopy(release["bundles"]["authoring"])
        victim = packs[-1].parent.relative_to(REPO).as_posix()
        include = f"{victim}/**"
        self.assertIn(include, spec["include"])
        spec["include"].remove(include)

        files = [
            path
            for path in build_bundles.tracked_or_untracked()
            if build_bundles.eligible(path, spec)
        ]
        version = (REPO / "library" / "VERSION").read_text(encoding="utf-8").strip()

        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "authoring.zip"
            build_bundles.write_bundle(archive, "authoring", version, files, spec)
            with zipfile.ZipFile(archive) as zipped:
                names = set(zipped.namelist())

        missing = authoring_pack_gaps(packs, names)
        self.assertIn(f"{victim}/pack.json", missing)
        self.assertIn(f"{victim}/SKILL.md", missing)

    def test_every_pack_has_a_per_pack_bundle(self) -> None:
        packs = pack_manifests()
        self.assertTrue(packs, "No pack manifests found under library/packs")
        release = json.loads(
            (REPO / "library" / "release.json").read_text(encoding="utf-8")
        )
        entry_gaps = build_bundles.pack_bundle_entry_problems(release)
        self.assertEqual(
            entry_gaps,
            [],
            "Per-pack bundle coverage failed:\n- " + "\n- ".join(entry_gaps),
        )
        problems: list[str] = []

        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "dist"
            for manifest in packs:
                pack_dir = manifest.parent
                pack_id = pack_dir.name
                bundle_name = f"pack:{pack_id}"
                relative = pack_dir.relative_to(REPO).as_posix()

                built = run(
                    str(TOOLS / "build_bundles.py"),
                    "--bundle",
                    bundle_name,
                    "--out",
                    str(out),
                )
                if built.returncode != 0:
                    problems.append(
                        f"{relative}: build failed: "
                        f"{(built.stderr or built.stdout).strip()}"
                    )
                    continue

                pack_version = json.loads(
                    manifest.read_text(encoding="utf-8")
                )["packVersion"]
                archive = out / f"counselor-pack-{pack_id}-v{pack_version}.zip"
                if not archive.exists():
                    problems.append(f"{relative}: missing archive {archive.name}")
                    continue

                with zipfile.ZipFile(archive) as zipped:
                    names = set(zipped.namelist())

                missing = sorted({"pack.json", "SKILL.md"} - names)
                if missing:
                    problems.append(
                        f"{relative}: {archive.name} missing root file(s): "
                        + ", ".join(missing)
                    )
                nested = sorted(name for name in names if name.startswith("library/"))
                if nested:
                    problems.append(
                        f"{relative}: {archive.name} keeps repository paths: "
                        + ", ".join(nested[:3])
                    )

        self.assertEqual(
            problems,
            [],
            "Per-pack bundle coverage failed:\n- " + "\n- ".join(problems),
        )

    def test_per_pack_guard_detects_a_removed_bundle(self) -> None:
        packs = pack_manifests()
        self.assertTrue(packs, "No pack manifests found under library/packs")
        release = json.loads(
            (REPO / "library" / "release.json").read_text(encoding="utf-8")
        )
        bundles = copy.deepcopy(release["bundles"])
        victim = packs[-1].parent
        bundle_name = f"pack:{victim.name}"
        self.assertIn(bundle_name, bundles)
        del bundles[bundle_name]

        gaps = build_bundles.missing_pack_bundle_entries({"bundles": bundles})
        relative = victim.relative_to(REPO).as_posix()
        self.assertIn(
            f"{relative}: no '{bundle_name}' entry in release.json",
            gaps,
        )

    def test_bundle_check_fails_without_a_per_pack_entry(self) -> None:
        release = json.loads(
            (REPO / "library" / "release.json").read_text(encoding="utf-8")
        )
        victim = pack_manifests()[-1].parent
        bundle_name = f"pack:{victim.name}"
        del release["bundles"][bundle_name]
        stderr = io.StringIO()

        with mock.patch.object(build_bundles, "read_json", return_value=release), \
            mock.patch.object(sys, "argv", ["build_bundles.py", "--check"]), \
            mock.patch("sys.stderr", new=stderr):
            status = build_bundles.main()

        self.assertEqual(status, 1)
        self.assertIn(
            f"no '{bundle_name}' entry in release.json",
            stderr.getvalue(),
        )

    def test_bundle_check_fails_with_a_stale_per_pack_entry(self) -> None:
        release = json.loads(
            (REPO / "library" / "release.json").read_text(encoding="utf-8")
        )
        bundle_name = "pack:not-a-real-pack"
        release["bundles"][bundle_name] = {
            "include": ["library/packs/not-a-real-pack/**"],
            "exclude": [],
        }
        stderr = io.StringIO()

        with mock.patch.object(build_bundles, "read_json", return_value=release), \
            mock.patch.object(sys, "argv", ["build_bundles.py", "--check"]), \
            mock.patch("sys.stderr", new=stderr):
            status = build_bundles.main()

        self.assertEqual(status, 1)
        self.assertIn(
            f"'{bundle_name}' has no matching pack directory",
            stderr.getvalue(),
        )

    def test_bundle_check_fails_with_a_mismatched_pack_include(self) -> None:
        release = json.loads(
            (REPO / "library" / "release.json").read_text(encoding="utf-8")
        )
        victim = pack_manifests()[-1].parent
        bundle_name = f"pack:{victim.name}"
        manifest_path = victim.relative_to(REPO).as_posix() + "/pack.json"
        release["bundles"][bundle_name]["include"] = [
            "library/packs/not-a-real-pack/**"
        ]
        stderr = io.StringIO()

        with mock.patch.object(build_bundles, "read_json", return_value=release), \
            mock.patch.object(sys, "argv", ["build_bundles.py", "--check"]), \
            mock.patch("sys.stderr", new=stderr):
            status = build_bundles.main()

        self.assertEqual(status, 1)
        self.assertIn(
            f"'{bundle_name}' does not select {manifest_path}",
            stderr.getvalue(),
        )


class CatalogTest(unittest.TestCase):
    def test_catalog_is_fresh(self) -> None:
        result = run(str(TOOLS / "build_catalog.py"), "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_packs_and_template_validate(self) -> None:
        result = run(str(TOOLS / "validate_pack.py"), "--all", "--template")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
