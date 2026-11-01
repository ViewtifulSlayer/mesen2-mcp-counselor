#!/usr/bin/env python3
"""Build a local catalog and SQLite FTS index from a user-supplied corpus.

No network. No OCR. ROMs, saves, manuals, maps, and patches are catalogued only.
Text is extracted from guides, websites, data, regional, and notes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from _common import CORPUS_ROOT, REPO_ROOT, rel, sha256_file

INDEX_CATEGORIES = {"guides", "websites", "data", "regional", "notes"}
CATALOG_ONLY = {"manuals", "maps", "saves", "roms", "patches"}
CATEGORY_NAMES = INDEX_CATEGORIES | CATALOG_ONLY
CATEGORY_ALIASES = {"gamefaqs": "guides", "docs": "data"}
TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".html", ".htm", ".csv", ".json", ".xml", ".log", ".ini", ".yaml", ".yml"}
ROM_SUFFIXES = {".smc", ".sfc", ".gb", ".gbc", ".gba", ".nes", ".pce", ".md", ".gen"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
SKIP_DIRS = {".index", ".git", "node_modules", "__pycache__"}
MAX_TEXT_BYTES = 5 * 1024 * 1024
CHUNK_CHARS = 1200
CJK_RE = re.compile(r"[\u3000-\u30ff\u3400-\u9fff\uff00-\uffef]")


def decode_bytes(raw: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "cp932", "shift_jis", "euc_jp"):
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    try:
        from charset_normalizer import from_bytes

        best = from_bytes(raw).best()
        if best is not None:
            return str(best), best.encoding or "unknown"
    except Exception:
        pass
    return raw.decode("latin-1", errors="replace"), "latin-1"


def html_to_text(raw: bytes) -> tuple[str, str, str]:
    text, encoding = decode_bytes(raw)
    title = ""
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        if soup.title and soup.title.string:
            title = " ".join(soup.title.string.split())
        body = soup.get_text("\n")
    except Exception:
        match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        if match:
            title = " ".join(re.sub(r"<[^>]+>", " ", match.group(1)).split())
        body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.I | re.S)
        body = re.sub(r"<[^>]+>", "\n", body)
    body = "\n".join(" ".join(line.split()) for line in body.splitlines())
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return title, body, encoding


def extract_text(path: Path) -> tuple[str, str, str]:
    raw = path.read_bytes()
    if path.suffix.lower() in {".html", ".htm"}:
        return html_to_text(raw)
    text, encoding = decode_bytes(raw)
    title = path.stem.replace("_", " ").replace("-", " ").strip()
    return title, text, encoding


def chunks(text: str, title: str) -> list[tuple[str, str]]:
    """Return (heading, chunk) pairs. Headings are lightweight and local."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    result: list[tuple[str, str]] = []
    heading = title
    buffer: list[str] = []
    size = 0
    for paragraph in paragraphs:
        if paragraph.startswith("#"):
            if buffer:
                result.append((heading, "\n\n".join(buffer)))
                buffer = []
                size = 0
            heading = paragraph.lstrip("#").strip()[:120] or title
            continue
        if size + len(paragraph) > CHUNK_CHARS and buffer:
            result.append((heading, "\n\n".join(buffer)))
            buffer = []
            size = 0
        buffer.append(paragraph)
        size += len(paragraph)
    if buffer:
        result.append((heading, "\n\n".join(buffer)))
    if not result:
        result.append((title, text[:CHUNK_CHARS]))
    return result[:200]


def category_for(rel_path: Path) -> str:
    parts = rel_path.parts
    first = parts[0] if parts else "other"
    return CATEGORY_ALIASES.get(first, first)


def kind_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in ROM_SUFFIXES:
        return "rom"
    if suffix in {".mss", ".sav", ".srm"}:
        return "save"
    if suffix in IMAGE_SUFFIXES:
        return "image"
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix in TEXT_SUFFIXES:
        return "text"
    return "binary"


def language_for(text: str) -> str:
    return "ja" if CJK_RE.search(text) else "en"


def resolve_game_root(root: Path, game: str | None) -> Path | None:
    """Accept a game folder, or the corpus root when --game selects one."""
    if any((root / name).is_dir() for name in CATEGORY_NAMES | set(CATEGORY_ALIASES)):
        return root
    if not game:
        return None
    matches = sorted(path for path in root.glob(f"*/{game}") if path.is_dir())
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(
            f"More than one {game} folder under {root}; pass the game folder directly:",
            file=sys.stderr,
        )
        for path in matches:
            print(f"  {path}", file=sys.stderr)
    return None


def game_label(root: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    pointer = root / "corpus.json"
    if pointer.exists():
        try:
            return json.loads(pointer.read_text(encoding="utf-8")).get("game", root.name)
        except Exception:
            pass
    return root.name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default=str(CORPUS_ROOT), help="corpus root or game folder")
    parser.add_argument("--game", help="game id; inferred from the folder or corpus.json otherwise")
    parser.add_argument("--out", default=str(CORPUS_ROOT / ".index"), help="index output directory")
    parser.add_argument("--max-bytes", type=int, default=MAX_TEXT_BYTES)
    parser.add_argument("--no-pointer", action="store_true", help="ignore corpus.json")
    args = parser.parse_args()

    root = Path(args.corpus).resolve()
    if not root.is_dir():
        print(f"Corpus not found: {root}", file=sys.stderr)
        return 2

    pointer = root / "corpus.json"
    if pointer.exists() and not args.no_pointer:
        try:
            source_root = json.loads(pointer.read_text(encoding="utf-8")).get("source_root")
        except Exception:
            source_root = None
        if source_root:
            candidate = Path(source_root)
            if not candidate.is_absolute():
                candidate = (REPO_ROOT / candidate).resolve()
            if candidate.is_dir():
                print(f"Following corpus.json pointer: {candidate}")
                root = candidate

    resolved = resolve_game_root(root, args.game)
    if resolved is None:
        print(
            "Corpus root must be a game folder with category subdirectories, "
            "or pass --game to select <platform>/<game> under it.",
            file=sys.stderr,
        )
        return 2
    if resolved != root:
        print(f"Using game folder: {rel(resolved)}")
        root = resolved

    game = game_label(root, args.game)
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / "index.sqlite"
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "CREATE TABLE catalog (path TEXT PRIMARY KEY, game TEXT, category TEXT, kind TEXT, "
        "size INTEGER, sha256 TEXT, title TEXT, lang TEXT, indexed INTEGER)"
    )
    conn.execute(
        "CREATE TABLE docs (id INTEGER PRIMARY KEY, path TEXT, game TEXT, category TEXT, "
        "title TEXT, heading TEXT, text TEXT, lang TEXT)"
    )
    conn.execute(
        "CREATE VIRTUAL TABLE docs_fts USING fts5("
        "path, game, category, title, heading, text, tokenize='unicode61')"
    )
    cjk_enabled = True
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE docs_cjk USING fts5("
            "path, game, category, title, heading, text, tokenize='trigram')"
        )
    except sqlite3.OperationalError:
        cjk_enabled = False
        print("Note: SQLite trigram tokenizer is unavailable; using unicode61 for CJK too.")

    catalog = []
    indexed_docs = 0
    indexed_files = 0
    skipped = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        rel_path = path.relative_to(root)
        if rel_path.name in {"README.txt", "corpus.json"}:
            continue
        if rel_path.suffix.lower() in {".pyc", ".pyo"}:
            continue
        category = category_for(rel_path)
        kind = kind_for(path)
        size = path.stat().st_size
        sha = sha256_file(path)
        title = path.stem.replace("_", " ").replace("-", " ").strip()
        lang = "en"
        indexed = False
        if (
            category in INDEX_CATEGORIES
            and kind in {"text", "html"}
            and size <= args.max_bytes
        ):
            try:
                title, body, _encoding = extract_text(path)
                title = title or path.name
                lang = language_for(body)
                for heading, chunk in chunks(body, title):
                    cursor = conn.execute(
                        "INSERT INTO docs(path, game, category, title, heading, text, lang) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (rel_path.as_posix(), game, category, title, heading, chunk, lang),
                    )
                    doc_id = cursor.lastrowid
                    conn.execute(
                        "INSERT INTO docs_fts(rowid, path, game, category, title, heading, text) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (doc_id, rel_path.as_posix(), game, category, title, heading, chunk),
                    )
                    if cjk_enabled and lang == "ja":
                        conn.execute(
                            "INSERT INTO docs_cjk(rowid, path, game, category, title, heading, text) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (doc_id, rel_path.as_posix(), game, category, title, heading, chunk),
                        )
                    indexed_docs += 1
                indexed = True
                indexed_files += 1
            except Exception as exc:  # keep the catalog useful even if one file fails
                print(f"  skip text extraction: {rel_path}: {exc}", file=sys.stderr)
                indexed = False
        else:
            skipped += 1
        catalog.append(
            {
                "path": rel_path.as_posix(),
                "game": game,
                "category": category,
                "kind": kind,
                "size": size,
                "sha256": sha,
                "title": title,
                "lang": lang,
                "indexed": indexed,
            }
        )

    conn.commit()
    conn.execute("INSERT INTO docs_fts(docs_fts) VALUES ('optimize')")
    if cjk_enabled:
        conn.execute("INSERT INTO docs_cjk(docs_cjk) VALUES ('optimize')")
    conn.commit()
    conn.close()

    meta = {
        "game": game,
        "root": rel(root),
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "files": len(catalog),
        "indexedFiles": indexed_files,
        "indexedChunks": indexed_docs,
        "catalogOnly": skipped,
        "cjkIndex": cjk_enabled,
        "index": rel(db_path),
    }
    (out / "catalog.json").write_text(
        json.dumps({"meta": meta, "files": catalog}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Indexed {indexed_files} file(s), {indexed_docs} chunk(s) from {len(catalog)} total.")
    print(f"Catalog: {out / 'catalog.json'}")
    print(f"Index:   {db_path}")
    print("The corpus and index are local-only. Do not commit them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
