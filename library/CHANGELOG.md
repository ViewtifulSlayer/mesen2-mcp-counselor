# Counselor Library Changelog

## 0.2.0 - 2026-11-03

First PC/Unity pack, additive harness contract, and a three-pack authoring bundle.

- Added the SaGa Frontier Remastered PC/Unity pack and the additive `target` and
  `harness` schema extension. Existing packs validate unchanged.
- Added the PC/Unity pack to the authoring bundle as a third worked example.
- Added bundle regression tests that require every shipped pack in the
  authoring archive and a matching per-pack archive with `pack.json` and
  `SKILL.md` at its root. Negative guard tests remove a pack include and a
  per-pack entry and assert both gaps are reported.
- `build_bundles.py --check` now fails when a shipped pack has no matching
  per-pack bundle entry, when a `pack:*` entry has no matching pack directory,
  or when an entry does not select that pack's `pack.json`.
- Added `.bin` to the forbidden-extension guard, so a save file cannot enter a
  pack or a release bundle.
- Documented harness packs in the authoring guide, installer, rubric, checklists,
  and release bundles.

## 0.1.0 - 2026-11-01

Initial library framework and reference pack.

- Added the pack contract, schemas, validator, catalog/page index, and release
  bundle builder.
- Added the local corpus scaffold, encoding-aware ingest, SQLite FTS index, and
  query tool.
- Added the `counselor-pack-author` master skill, seven lessons, rubric, code,
  checklists, and template.
- Added the Final Fantasy Legend pack: route/world, systems, battle data, harness,
  schematics, Lua kit, field test, and public/local source manifests.
- Added the Secret of the Stars pack: systems, world topology, starter data,
  RAM notes, regional variants, and intake case study.
- Added CI validation and tagged library release bundles.
- No ROMs, guides, manuals, maps, saves, or third-party text are included.
