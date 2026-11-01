# The local corpus

The corpus is the user's own reference shelf. It is empty in a fresh clone and
is gitignored. Nothing here is distributed: no guide text, no manual scans, no
map renders, no ROMs, no saves, no patches.

The public library works without it. A pack is written from verified
observations, original prose, and facts derived from the ROM. The corpus is the
second layer: when you already own reference material, the agent can query it
directly instead of re-deriving everything or searching the web.

## Layout

```text
library/corpus/<platform>/<game>/
  guides/     walkthroughs, FAQs, boss guides
  manuals/    manual scans, PDFs, page images
  maps/       screenshots, rendered maps, tile maps
  data/       CSV/JSON, RAM notes, technical documents
  websites/   mirrored sites
  regional/   JP, EU, and other regional sources
  saves/      savestates, SRM, battery saves
  roms/       your ROMs, hashed for identification only
  patches/    IPS/BPS patches and patch documentation
  notes/      your own observations
```

Create the scaffold with:

```bash
python library/tools/scaffold_corpus.py --platform snes --game secret-of-the-stars
```

If the material already lives somewhere else, point at it instead of copying it:

```bash
python library/tools/scaffold_corpus.py --adopt ../my-sources/secret-of-the-stars \
  --platform snes --game secret-of-the-stars
```

That writes `corpus.json` with a local pointer. `ingest_corpus.py` follows the
pointer unless you pass `--no-pointer`. Add `--move` only when you want the
categories moved into the canonical scaffold.

## What gets indexed

| Category | Treatment |
|---|---|
| `guides/`, `websites/`, `data/`, `regional/`, `notes/` | Text is extracted and indexed in SQLite FTS5 |
| `manuals/`, `maps/`, `saves/`, `roms/`, `patches/` | Catalogued only: path, size, SHA-256, kind, language |

Text files are decoded as UTF-8, then CP932/Shift_JIS, then EUC-JP, then a
best-effort detector. Japanese text goes into a trigram index when the SQLite
build supports it, so a query like `魔王` still finds the page. HTML is stripped
to text and its `<title>` is kept.

```bash
python library/tools/ingest_corpus.py --corpus library/corpus --game secret-of-the-stars
python library/tools/query_corpus.py "town data" --game secret-of-the-stars
python library/tools/query_corpus.py "魔王" --game secret-of-the-stars
```

`ingest_corpus.py` accepts either the game folder or the corpus root plus
`--game`. An adopted folder may keep its old `gamefaqs/` and `docs/` names; those
are indexed as `guides/` and `data/`.

The catalog is `library/corpus/.index/catalog.json`; the index is
`library/corpus/.index/index.sqlite`. Both are local.

## Legal and privacy rules

- Do not commit the corpus or the index. The repository ignores them.
- Do not add download links, scrapers, or mirrors of copyrighted material to
  the public tree. The corpus is for material the user already has.
- Facts learned from a source can go into a pack. Text cannot. Credit the source
  by title, author, and license in the pack's public manifest.
- A source that forbids redistribution stays local-only. Its URL, path, hash,
  byte count, and page list stay in `sources/manifest.local.json`, which is also
  gitignored.
- Manuals and maps are catalogue-only by default. Open a page when a specific
  question needs it, not to browse.
- ROMs are hashed for identification. They are never copied into a pack and
  never uploaded.

## What a pack may say about a corpus

A pack's `pack.json` names its expected corpus location:

```json
"corpus": { "platform": "snes", "game": "secret-of-the-stars" }
```

That is a hint for the authoring agent, not a dependency. A pack must remain
usable with no corpus at all. If a claim depends on a source the user has not
provided, mark it `[U]` and say what is missing.
