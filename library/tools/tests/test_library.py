"""Unit and integration tests for the Counselor Library tools.

Run from the repository root:

    python -m unittest discover -s library/tools/tests -v

The fixtures are original text. They exist to exercise decoding, indexing,
cataloguing, validation, installation, and bundling without any copyrighted
material.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REPO = TOOLS.parents[1]
TEMPLATE = REPO / "library" / "academy" / "templates" / "game-pack"
FIXTURE_CORPUS = Path(__file__).resolve().parent / "fixtures" / "corpus"

sys.path.insert(0, str(TOOLS))

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
        rom.write_bytes(b"not a rom")
        self.assertTrue(any("forbidden extension" in item for item in self.errors()))


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


class CatalogTest(unittest.TestCase):
    def test_catalog_is_fresh(self) -> None:
        result = run(str(TOOLS / "build_catalog.py"), "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_packs_and_template_validate(self) -> None:
        result = run(str(TOOLS / "validate_pack.py"), "--all", "--template")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
