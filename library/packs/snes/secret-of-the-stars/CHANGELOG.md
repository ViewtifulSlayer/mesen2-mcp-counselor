# Changelog

## 0.2.3 - 2026-11-01

- Pushed the Brasca route past the entrance and probed the Ancient Well
  directly. The ring is drawn behind a continuous hedge; 154 walked positions
  produced no `$040E` change, and the local door table has no Brasca row into
  `$00BC` or `$0146`. The well is located, not enterable from town.
- Decoded `$02AC`-`$02AF` as the player coordinate: big-endian X and Y, 16
  units per tile, page-local, and writable. Replaced the "not decoded" note.
- Withdrew the earlier Sealed Cave claim. `$00C0` is a stub corridor that ends
  on a one-tile platform in the void and has no exit to the well.
- Updated `references/world.md`, `references/harness.md`, and
  `tests/field-test.md`; the certification score moved from 92 to 91.
- No host code changed.

## 0.2.2 - 2026-11-01

- Added inline `[V]`, `[D]`, and `[U]` tags to the systems and harness claims,
  with a per-row evidence column for the hero record.
- Raised the evidence category from 22/25 to 25/25 and the total from 89/100 to
  92/100. No factual claim changed.

## 0.2.1 - 2026-11-01

- Certified on Mesen2 MCP 0.6.0 at 89/100. Rights failures: 0.
- Recorded the rubric deductions: partial coverage beyond Ray's House and
  Brasca, prose labels instead of inline tags on some systems and harness
  claims, and the battle run's dependency on a local level-25 save.
- No claims changed in this pass; this release records the score and status.

## 0.2.0 - 2026-11-01

- Ran the field test on Mesen2 MCP 0.6.0 against the USA ROM. The pack is now
  `verified`.
- Verified `$0020`, `$0053`, `$040E`, `$043C`, `$04A4`-`$04AE`, `$04BD`,
  `$0D1F`, `$0D21`, and the `$5000` hero table against screen values.
- Corrected the hero stride to `$36` and the spell slots to seven
  (`$5026`-`$502C`). The old page stopped at five and said the stride was not
  asserted.
- Clarified that `$5007` is a rank tier, not the job label in `characters.csv`.
  Ray, Tina, Cody, and Leona read `01` (Pennon) at Brasca; Dan read `04`.
  The Lua kit now decodes the name and exposes the rank and the seven spell
  bytes.
- Clarified that `$043C` keeps the last encounter on the field and that
  `$0D1F`/`$0D21` are battle pools, not total gold. The Lua kit now exposes
  `battleGold` and `battleEp`; `gold` and `ep` remain aliases.
- Recorded `$04AE = E0` with five Kustera members; the notes' `2X`/`4X` pair
  is not the whole mask.
- Split the harness page into verified, observed-but-undecoded, and still
  unverified addresses. The blanket "documented, not live-verified" caveat is
  gone.
- Recorded map ids `$0026` (Ray's House) and `$00B8` (Brasca).
- No host code changed.

## 0.1.1 - 2026-11-01

- Fixed both recipes to load `sots_kit` with `-- includes:`. `-- requires:` is
  a kit-module header; using it in a recipe leaves the kit unloaded.
- No live verification yet; the pack remains `draft`.

## 0.1.0 - 2026-11-01

- Initial draft pack from the local Landmine36 technical document, GameFAQs
  guides, RPGClassics shrine, RetroMaggedon guide, JP Aqutallion guide, manuals,
  and map set.
- Added the overview, world, systems, data, harness, and edge-case references.
- Added starter character, enemy, item, spell, shop, map-id, and encounter
  tables with provenance.
- Added the JP/US variant notes and item-name differences.
- Added the original world schematic, Lua kit, and two probe recipes.
- Added the field-test procedure; live verification pending.
