# Lesson 2 - Inventory the corpus

## Goal

Know what sources exist before deciding what to read.

## Do this

```bash
python library/tools/scaffold_corpus.py --platform snes --game secret-of-the-stars
python library/tools/ingest_corpus.py --corpus library/corpus --game secret-of-the-stars
```

Read `library/corpus/.index/catalog.json`. It records every file, its category,
size, hash, language, and whether it was indexed.

Then query:

```bash
python library/tools/query_corpus.py "map id" --game secret-of-the-stars
```

## What the categories mean

| Category | Use |
|---|---|
| `guides/` | walkthroughs, FAQs, boss guides |
| `manuals/` | scans, PDFs, page images |
| `maps/` | screenshots, renders, tile maps |
| `data/` | CSV/JSON, RAM notes, technical docs |
| `websites/` | mirrored sites |
| `regional/` | JP/EU/other-language sources |
| `saves/` | savestates, SRM |
| `roms/` | the user's ROMs, hashed only |
| `patches/` | IPS/BPS and patch docs |
| `notes/` | your own observations |

## Rules

- Do not commit the corpus. It is gitignored.
- Do not browse manual scans by default; catalogue them and open a page only when
  the question needs it.
- A source you did not consult should not be in the manifest. A source you
  consulted but did not use should still be credited.
- If a file is not indexed, say so; do not pretend the index searched it.

## Check

- `catalog.json` exists and lists the expected categories.
- The index count is plausible for the text sources, not the manuals.
- The JP HTML is decoded, not mojibake.
- Every file you plan to cite has a stable relative path.

## Common failure

The corpus has 315 MB of manual scans and 17 MB of websites. Indexing everything
makes the first query slow and the index noisy. Catalog the manuals and maps;
index the text.
