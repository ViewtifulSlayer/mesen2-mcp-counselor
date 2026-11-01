---
name: ffl-gameplay
description: Player-perspective and technical context for Final Fantasy Legend (GB): route order, encounter areas, battle menu traps, monster HP tables, memory probes, and Lua recipes. Use when playing, testing, reverse-engineering, or patching the ROM.
---

# FFL Gameplay: context for playing and probing the ROM

This pack is for work on *Final Fantasy Legend* (Game Boy, USA, 128 KiB
vanilla ROM). It gives the agent enough context to act without wandering:
where the exits are, what the battle menu is doing, how monster HP is built,
what the battle record contains, and which probes are reliable.

There are no spoiler gates. Read what the task needs.

## Read by task

| Task | Read |
|---|---|
| First contact, play, walk the map | [overview](references/overview.md), [world](references/world.md) |
| Name a battle record or predict HP | [data](references/data.md), [systems](references/systems.md) |
| Plan a route or find an area | [world](references/world.md) |
| Debug a menu trap or a stalled walk | [systems](references/systems.md), [edge cases](references/edge-cases.md) |
| Patch, script, or harvest encounters | [harness](references/harness.md), [data](references/data.md) |
| Compare the Japanese release | [variants](variants/differences.md) |

## 60-second orientation

- **ROM:** vanilla USA, 131,072 bytes, SHA-1
  `901dfc83c72e172d35a376835807fc788444a9bb`, MBC2. Certified on Mesen2 MCP
  0.5.2 and 0.6.0.
- **Start:** load the ROM, press START, mash A through the intro. About 900
  frames gets onto the world map. Save a state there; it is the clean baseline.
- **Movement:** directions move; A talks/confirms; B backs out and opens the
  field menu.
- **Battle menu:** `FIGHT` / `ABIL` / `RUN`. The middle `ABIL` row renders
  invisibly, so the hand looks like it is on `FIGHT` while the selection is one
  row lower. A on `ABIL` opens an empty window for a non-caster and looks frozen.
  B backs out; DOWN + A selects `RUN`.
- **Area probe:** HRAM `$FFBD` is the current map's encounter id. Log it every
  frame and a walk becomes a survey of area boundaries.
- **Battle probe:** 32-byte records at `$D000`; slots 0-3 are the party, slot 4
  (`$D080`) is the first enemy. `+31` is the crtype index.
- **HP:** a monster's HP is `hpvalues[crtype[i][1]]` minus a random `0..(v >> 4)`,
  so it is always in `[v - (v >> 4), v]`. A point or two below the guide is
  variance, not an error.

## Source IDs

`[S:id]` means "this came from a recorded source." The public manifest records
the title, author, and license. Local-only sources keep their URLs and paths in
`sources/manifest.local.json`, which is gitignored.

The pack is self-contained: if a local source is absent, the synthesized
references and the verified tables still work. If the source is present, the
reading plan points to the exact section.

## Corpus status

If this repository has a populated local corpus:

```bash
python library/tools/query_corpus.py "bridge east" --game final-fantasy-legend
```

If it does not, use this pack directly. The local corpus adds the original guide
text and the Terran map sheets; it is not required for the route, the battle
record layout, or the HP table.

## Pages

| Page | What it answers |
|---|---|
| [Overview](references/overview.md) | ROM identity, controls, save behavior, scope |
| [World](references/world.md) | Route order, bridge geometry, map reading, known gaps |
| [Systems](references/systems.md) | Battle menu, records, HP construction, encounters |
| [Data](references/data.md) | HP ladder, confirmed monsters, encounter table |
| [Harness](references/harness.md) | Mesen MCP probes, Lua, batching, state hygiene |
| [Edge cases](references/edge-cases.md) | The traps that cost real time |
| [Regional differences](variants/differences.md) | JP/US title and verification status |

## Quick checks

- Names not matching stats? The guide writes crtype indices in **hex** inside
  brackets. `LIZARD [42]` is decimal 66.
- HP one or two below the guide? Expected. Check `v - (v >> 4)`.
- Detector firing in the field? `$D000` is not a field probe. Gate on the four
  party records (`$40` at `$D000`, `$D020`, `$D040`, `$D060` plus sane HP).
- Recipe fails with `global 'ffl'` nil? The header says `-- requires:`; use
  `-- includes: ffl_kit`.
- Walk not progressing? Check which scroll axis is frozen. A pinned SCY means
  the map is one screen tall and the exits are east/west.
- Battle looks frozen after A? You are on the empty `ABIL` row. Press B, then
  DOWN + A to run.

## What not to put in this pack

ROMs, patched ROMs, save states, guide text, map renders, or manual scans. Those
stay local. See `library/LICENSING.md`.
