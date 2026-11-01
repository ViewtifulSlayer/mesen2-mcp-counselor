# Contributing

This fork adds the Counselor Library under `library/`. The emulator and MCP
server at the repository root come from
[Azarem/mesen2-mcp](https://github.com/Azarem/mesen2-mcp); send host, build, and
server bugs upstream unless the fork caused them.

## Ways to contribute

| Contribution | Start here |
|---|---|
| A new game pack | Read `library/academy/SKILL.md`, then lessons 1-7 |
| A correction to an existing pack | Open the "Pack correction" issue form with the page and evidence |
| A source you own and can share | Open the "Source intake" issue form; do not attach the file |
| A tool or schema improvement | Open a PR against `library/tools` or `library/schemas` |
| A rights concern | See `library/TAKEDOWN.md` |

## Ground rules

- **No copyrighted files.** Do not commit ROMs, patched ROMs, saves, savestates,
  manuals, map renders, guide text, wiki text, or ripped art. This includes
  screenshots of guide pages and "small" excerpts.
- **Facts, not expression.** A stat, a formula, an item price, or an encounter
  rate can be recorded. A guide's prose, table layout, or walkthrough structure
  cannot be copied.
- **Credit what you consulted.** Every source in a public manifest has a title,
  author, license, redistribution status, region, and language. Local-only
  sources keep their URL, path, and hash in `sources/manifest.local.json`, which
  is gitignored.
- **Declare gaps.** `[U]` is an acceptable tag. An honest `partial` pack is better
  than an invented `verified` one.
- **No scrapers, mirrors, or download links.** The corpus is for material the
  user already owns.

## Before opening a pack PR

```bash
python -m pip install -r library/tools/requirements.txt
python library/tools/validate_pack.py --all --template
python library/tools/build_catalog.py --check
python -m unittest discover -s library/tools/tests -v
python library/tools/build_bundles.py --check
```

Also:

- The pack's `SKILL.md` frontmatter name matches `pack.json` `skill.name`.
- Every reference page has `title`, `summary`, `coverage` frontmatter.
- Every citation `[S:id]` resolves in `sources/manifest.public.json`.
- Every declared data file has a provenance entry with the current SHA-256.
- `tests/field-test.md` records a real procedure and result, or the pack is not
  `verified`.
- `CERTIFICATION.md` has `Score: NN/100` and `Rights failures: 0` before a pack
  claims `certified`.

Do not edit `library/CATALOG.md`, `library/PAGE_INDEX.md`,
`library/ATTRIBUTIONS.md`, or `library/catalog.json` by hand. Run
`build_catalog.py` and commit the regenerated files.

## Upstream sync

- The fork keeps the upstream tree at the repository root. Library changes belong
  under `library/`.
- Do not bump `mcp-version.txt` for a library change. Library releases use
  `library-v*` tags; see `library/UPSTREAM.md`.
- Do not change host code in a pack PR. Open a separate proposal first.
- Keep the conflict surface to `README.md` and `.gitignore`, and record new
  divergences in `library/UPSTREAM.md`.

## Commit and PR style

- One pack or one tool change per PR when possible.
- Describe what you verified and how (server version, ROM SHA-1, exact values).
- State what remains unverified.
- By contributing, you agree that prose, data compilations, schematics, and
  variants are licensed CC BY-SA 4.0 and code is GPL-3.0, as described in
  `library/LICENSING.md`. Only submit work you can license that way.
