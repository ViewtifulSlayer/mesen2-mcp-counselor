# Changelog

## 0.2.1 - 2026-11-01

- Replayed a fresh 0.6.0 boot: START at the title, mash A, world map at frame
  1709, `field=true`, encounter `$00`.
- Saved `ffl-clean-world-0.6.0.mss` and confirmed it reloads with a matching
  sidecar and the same field result.
- Raised the certification score to 97/100; reproducibility is now 20/20.
- Documented the frame-counter difference between the 0.5.2 baseline (1901) and
  the fresh 0.6.0 boot (1709).

## 0.2.0 - 2026-11-01

- Certified on Mesen2 MCP 0.6.0 (Mesen 2.1.1) at 96/100.
- Recorded the 0.6.0 field test: clean-state load, south-forest `$11`, battle
  `$12`, ZOMBIE crtype `$78` HP 58/58, and party HP matching the status window.
- Fixed both recipes to load the kit with `-- includes:`; `-- requires:` is a
  kit-module header, not a recipe header.
- `reach-field` now reports party HP only in battle. In the field `$D000` is the
  tilemap, and the old output read tiles as HP.
- Corrected the field-test expectations for the clean baseline: encounter `$00`
  and empty party HP are valid in the field.
- Added the recipe-header trap to the edge cases and harness pages.

## 0.1.0 - 2026-11-01

- Initial pack converted from the verified FFL project's `ffl-gameplay` skill.
- Added the overview, world, systems, data, harness, and edge-case references.
- Added the HP ladder, confirmed monster table, and world-1 encounter table with
  provenance.
- Added the original overworld schematic, Lua kit, and two recipes.
- Added public source credits and a topic-level reading plan.
- Field test documented from 0.5.2 evidence; 0.6.0 re-run was pending at release.
