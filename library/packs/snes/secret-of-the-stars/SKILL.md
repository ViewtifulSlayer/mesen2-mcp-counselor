---
name: sots-gameplay
description: Player-perspective and technical context for Secret of the Stars (SNES): party structure, colony system, battle and menu flow, route topology, starter data tables, RAM probes, and JP/US differences. Use when playing, testing, reverse-engineering, patching, or localizing the ROM.
---

# Secret of the Stars: context for playing and probing the ROM

This pack is for *Secret of the Stars* (SNES, USA, 1.5 MiB LoROM) and its
Japanese release, *Aqutallion*. It gives the agent enough context to act without
wandering: the Aqutallion/Kustera party split, the menu and battle flow, the
route topology, the starter data tables, and the core RAM probes verified on
Mesen2 MCP 0.6.0.

There are no spoiler gates. Read what the task needs.

## Read by task

| Task | Read |
|---|---|
| First contact, play, choose a route | [overview](references/overview.md), [world](references/world.md) |
| Understand a menu, battle, or colony | [systems](references/systems.md) |
| Name a value or look up a starter table | [data](references/data.md) |
| Probe RAM or write a Lua recipe | [harness](references/harness.md) |
| Debug a mismatch or an unverified address | [edge cases](references/edge-cases.md) |
| Compare the Japanese release | [variants](variants/differences.md) |

## 60-second orientation

- **ROM:** USA, 1,572,864 bytes, SHA-1
  `958a0a835e2e39f382cb37a99098a3cdd4812cf7`, LoROM.
- **Two parties:** the Aqutallion heroes (Ray, Tina, Cody, Leona, and recruits)
  and the Kustera colony party. The field menu controls one at a time; the
  verified party slots are at `$04A4` and `$04A9`.
- **Battle flow:** the battle menu exposes Attack, Defend, Item, Spells, and
  Unity. Unity magic is a timed/leader-based combination, not an ordinary spell.
- **Colony:** Kustera is a town-building layer, not just a second party. It has
  its own recruitment, buildings, and party size (`$04BD`).
- **Map probe:** `$040E` is the 16-bit map id; `$043C` is the 8-bit encounter
  id. Verified values: `$0026` Ray's House and `$00B8` Brasca. The encounter id
  keeps the last battle's value on the field.
- **Battle probe:** `$0020` reads `01` outside battle and `05` entering battle,
  in battle, and on the victory screen. `$0053` is the game state (`0` field,
  `2` entering, `3` battle, `4` victory).
- **Hero records:** all 16 start at `$5000` with a `$36` stride. Each starts
  with a seven-byte name, has a rank tier at `+$07`, and seven spell bytes at
  `+$26`-`+$2C`, not five.
- **Battle pools:** `$0D1F` and `$0D21` are battle gold and EP, not the save's
  total money.
- **Data:** the starter tables cover 16 characters, 16 enemies, 20 items, 12
  spells, 12 shops, 20 map ids, and 8 encounter packs. The full 35 CSV set stays
  local.

## Source IDs

`[V]` is a live field-test value on the named ROM and server. `[D]` is a value
derived from a documented table, manual, or guide, with provenance recorded in
`data/provenance.json` or the public manifest. `[U]` is unverified: a local-note
claim, an open question, or an observation whose layout is not decoded.
`[S:id]` is a recorded source. The public manifest has the title, author, and
license. Local-only sources keep URLs and paths in `sources/manifest.local.json`,
which is gitignored.

This pack is useful without the local corpus. The local corpus adds the full
technical CSVs, the JP guide, the scans, and the map renders; it is not required
for the starter tables or the route outline.

## Corpus status

If the local corpus is populated:

```bash
python library/tools/query_corpus.py "map id" --game secret-of-the-stars
python library/tools/query_corpus.py "町データ" --game secret-of-the-stars
```

If it is absent, use this pack directly. The JP guide is Shift_JIS; the ingest
tool detects it.

## Pages

| Page | What it answers |
|---|---|
| [Overview](references/overview.md) | Release identity, controls, party model, scope |
| [World](references/world.md) | Route outline, locations, map ids, known gaps |
| [Systems](references/systems.md) | Party, colony, battle, menus, shops, status |
| [Data](references/data.md) | Starter tables and how to extend them |
| [Harness](references/harness.md) | Verified RAM addresses, hero layout, and Lua probes |
| [Edge cases](references/edge-cases.md) | Verified probe traps, LoROM, region traps |
| [Regional differences](variants/differences.md) | JP/US title, names, and open comparisons |

## Quick checks

- A party slot reads `FF`? That slot is empty; do not treat it as party member 0.
  Ray's House reads `[00,FF,FF,FF,FF]`; `00` is Ray.
- `$04A4` through `$04A8` are the Aqutallion slots; `$04A9` through `$04AD` are
  Kustera. Mixing them produces a plausible but wrong party.
- Map id is 16-bit, not 8-bit. Reading one byte gives a value that may look
  valid; read `$040E` and `$040F` together.
- Hero records start at `$5000` with a `$36` stride. Hero 0 is not the whole
  party; the table has all 16 characters.
- A nonzero encounter id on the field is the last encounter, not an active
  battle. Check `$0020` and `$0053`.
- Battle gold and EP read `0` on the field even with a rich save. They are
  pools, not the wallet.
- The JP and US releases have different sizes and character sets. Do not apply a
  US address to a JP dump without a live check.

## What not to put in this pack

ROMs, patched ROMs, save states, guide text, manual scans, map renders, or the
full technical CSV set. Those stay local. See `library/LICENSING.md`.
