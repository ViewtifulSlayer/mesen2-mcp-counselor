---
name: counselor-pack-author
description: Author a Counselor game pack from a ROM, a PC/Unity build, or user-supplied sources. Use when asked to create, extend, verify, or review a game-context pack for Mesen2 MCP, or to turn a local corpus into a pack without copying copyrighted material.
---

# Counselor pack author

You are building a **context pack**, not a hint line. A pack gives an agent
enough grounded context to play, test, reverse-engineer, patch, or localize a
specific game. It does not gate hints or hide answers. It does make the agent's
claims traceable.

## Inputs to ask for

- Game title, platform, region, and the exact ROM if available.
- For a PC/Unity target, the executable, Unity version, scripting backend,
  metadata version, and asset hashes instead of a ROM.
- The task the pack should support: play/test, reverse engineering, patching,
  localization, or a mix.
- The local corpus path, if one exists.
- Any known gaps: areas not reached, tables not verified, regional versions.

Do not ask for download links. If a source is missing, ask whether the user has a
copy and name the corpus category it belongs in.

## Workflow

1. **Identify the edition.** Get the ROM title, size, SHA-1, mapper, and region.
   For a PC/Unity target, record a `target` build identity instead: executable,
   `GameAssembly.dll`, metadata, `resources.assets`, Unity version, scripting
   backend, and metadata version. If the identity is unavailable, mark it `[U]`.
2. **Inventory the corpus.** Run `scaffold_corpus.py` if needed, then
   `ingest_corpus.py`. Read `catalog.json`; query the index for the topics you
   need. If there is no corpus, work from the sources the user provides.
3. **Triage sources.** For each source, record title, author, license, region,
   language, and whether it is repo-safe or local-only. Prefer the ROM as the
   authority, the technical docs second, and prose guides third.
4. **Read the game before the guides.** Get the controls, the first goal, the
   menu structure, and one verified map transition. Do not write a route from a
   guide alone if you can walk it.
5. **Create `pack.json`.** Copy the template. Set honest coverage. A pack with
   declared gaps is better than a pack with invented completeness.
6. **Write `SKILL.md` first.** The 60-second orientation and the read-by-task
   table decide whether the pack is usable. Then write the six references:
   `overview`, `world`, `systems`, `data`, `harness`, `edge-cases`.
7. **Tag every claim.** `[V]` verified in Mesen/ROM or against the target's
   fixture, `[D]` derived from game data, `[S:id]` sourced, `[U]` unverified. If
   a claim has no tag, it is not ready.
8. **Derive data, do not copy it.** Put facts in `data/*.csv` with a schema you
   chose. Record the origin, source, generator, hash, and verification date in
   `data/provenance.json`. Never paste a guide's table wholesale.
9. **Draw schematics where the pack has a spatial model.** Use original SVG for
   room graphs, routes, and indexes. Do not trace tile maps or commit rendered
   maps.
10. **Write probes or a harness.** For a cartridge target, put the kit in
    `lua/lib/<game>_kit.lua` and recipes in `lua/lib/recipes/`; use
    `-- requires: <kit>` in recipes. For a PC/Unity target, put a stdlib script
    in `harness/` and declare `harness` instead of `lua`. Test in Mesen or
    against the fixtures if available; otherwise mark the probe `[U]`.
11. **Build the public and local manifests.** Public: title, author, license,
    redistribution, covers, region, language. Local: URL, path, hash, bytes,
    retrieved. Never put URL/path/hash in the public manifest for `local-only`.
12. **Validate.** Run `validate_pack.py`, `build_catalog.py --check`, and the
    unit tests. Fix errors; do not suppress them.
13. **Field-test.** Run `tests/field-test.md` on the target ROM. Record the
    server version and exact values. If you cannot run it, leave the pack
    `verified` or `draft`, not `certified`.
14. **Review.** Score with `rubric.md`. A rights failure blocks certification.
15. **Hand off.** Tell the user what is verified, what is pending, and what
    should not be committed.

## Source request behavior

If a needed source is absent:

1. Name the gap and why it matters.
2. Ask the user whether they have a copy.
3. Name the corpus category (`guides/`, `manuals/`, `maps/`, `data/`,
   `websites/`, `regional/`, `notes/`).
4. If they do not, proceed with the public synthesis and mark the missing claim
   `[U]`.

Never provide a download link, scrape a site, or reconstruct a guide from memory
and present it as sourced.

## Rights rules

- Do not commit ROMs, patched ROMs, saves, manuals, map renders, guide text, or
  ripped art.
- Do not include CC BY-NC-SA text. Do not include GameFAQs or Fandom text.
- Facts are okay; expression is not. Re-derive tables with your own schema.
- Use original schematics, not traced maps.
- Public credit is title/author/license only for local-only sources.
- A permissioned inclusion needs a record in `library/permissions/`.

## Definition of done

- `pack.json`, `SKILL.md`, six references, three variant pages, data with
  provenance, public/local manifests, original schematics where applicable, and
  a field test exist, plus either a Lua kit/recipes or a declared harness.
- The PC/Unity example is `library/packs/pc/saga-frontier-remastered`; it uses
  `target` and `harness` instead of `rom` and `lua`.
- `validate_pack.py` passes.
- The catalog and page index are fresh.
- The field test either passes or is explicitly pending.
- No forbidden file is in the pack.
- `CERTIFICATION.md` exists if the status is `certified`.

## Commands

```bash
python library/tools/validate_pack.py --pack <id>
python library/tools/build_catalog.py --check
python library/tools/scaffold_corpus.py --platform <platform> --game <id>
python library/tools/ingest_corpus.py --corpus library/corpus --game <id>
python library/tools/query_corpus.py "<topic>" --game <id>
python library/tools/install_pack.py --pack <id>
```
