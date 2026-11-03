---
name: sfr-save-mapping
description: Save-data mapping and reverse-engineering context for SaGa Frontier Remastered (PC/Steam, Unity 2019.4.16f1 IL2CPP). Use when parsing SaveData.bin, mapping pty/ply/eventwk/mapwk fields, resolving item, ability, map, area, shop or monster IDs, checking flag bytes, INIT sets, Mec/Mystic/Monster records, or planning a runtime probe.
---

# SaGa Frontier Remastered: save-data mapping context

This pack is for the PC/Steam release of *SaGa Frontier Remastered* (Unity
2019.4.16f1, IL2CPP metadata v24). It is scoped to save-tool engineering and
data mapping, not to a walkthrough. It gives an agent the container model, the
field-status table, the ID namespaces, the documented traps, and a save-file
lab that runs without the game.

## 60-second orientation

- **Save container:** raw DEFLATE (RFC 1951), no zlib or gzip header. Inflate
  to JSON, then parse `saveDataList[n].saveDataJsonStr` a second time. `[V]`
- **Snapshots:** 59 numbered slots plus quick and auto, 61 entries. Quick and
  auto are independent snapshots, not mirrors of the active slot. `[V]`
- **Party:** `pty.psnCnt`, `pty.heroNo`, and three 56-byte arrays; `ply` holds
  41 roster records in every save, so presence is not party membership. `[V]`
- **Location:** `mapwk.imfName` is the current room; `eventwk.mapNo` is the
  previous map; `mapwk.map_name` and slot `MapNumber` are 0-based area
  indexes. `[V]`
- **Flags:** `pty.snroFlg` is 512 bytes, a mix of bit fields and counters, not
  booleans. 169 bytes are named. `[V]`
- **Integrity:** `sfSys.chk*` and `sum` are unmapped. Do not recompute them.
  `[V]`
- **Build:** Unity 2019.4.16f1, IL2CPP metadata 24, Steam app 1295270. The six
  measured hashes are in `data/unity-build.csv`. `[V]` `[S:pcgamingwiki-sfr]`

## Read by task

| Task | Read |
|---|---|
| Start, orient, or decide what to trust | [Overview](references/overview.md) |
| Decode a location, room, area, or map ID | [World](references/world.md) |
| Decode party, roster, flags, shops, INIT, races | [Systems](references/systems.md) |
| Name an ID or look up a table count | [Data](references/data.md) |
| Inflate, diff, or assert a save; plan a live probe | [Harness](references/harness.md) |
| Debug a mismatch or an unverified field | [Edge cases](references/edge-cases.md) |
| Compare English/Japanese assets or PS1/Remastered | [Variants](variants/differences.md) |

## Source and evidence tags

`[V]` is verified against a named fixture, a measured build value, or a table
that the save tool's harness gates. `[D]` is derived from a documented table or
an asset, with the table named in `data/` or the reference. `[S:id]` is a
recorded source; the public manifest has the title, author, and license, and
the local manifest has the URL or path. `[U]` is unverified or open.

The pack is useful without the local corpus. The local corpus adds the full
save-tool runbook, the 6.57 MB community gameinfo tree, the fixtures, and the
installed game files. Those are not required for the field map or the lab.

## Hard traps

- `eventwk.mapNo` is the **previous** map. `mapwk.imfName` is the current
  room. `mapwk.map_name` and slot `MapNumber` are area indexes, not room IDs.
- `sfSys.parLev` is the new-scenario starting Battle Rank, not the last-clear
  rank and not an active-slot mirror.
- `pty.parLev` does not exist. The live value is `pty.each.parLev`.
- `getskill` is a 64-byte bit grid, MSB-first:
  `ability_id = (byte - 0x38) * 8 + bit`.
- The save stores `hpMax` only. There is no current-HP field in `ply`.
- `quickSaveData` and `autoSaveData` are independent; diff them, do not assume
  they share the active slot's map or play time.
- `IsTakeover` is the NG+ carry-over marker, not a completion flag.
- `chrNo` 0x40 is a real roster record with no character name-table entry.
- Room ID 425 (`0x1A9`) is a gap in the community map table.
- The `chk*` and `sum` fields have no known algorithm. Recompression is not
  byte-identical to the game's writer.

## Install and harness

```bash
python library/tools/install_pack.py --pack pc/saga-frontier-remastered --target .agents/skills
```

This pack has no Lua kit and no `--mcp-lib-dir`. Its harness is
`harness/save_lab.py`, and its runtime bridge plan is in
`references/harness.md`.

```bash
python harness/save_lab.py assert-fixture --fixture asellus \
  --input ../saga-frontier-save-tool/docs/pre-research/SaveData.bin.json
python harness/save_lab.py assert-fixture --fixture t260g \
  --input ../saga-frontier-save-tool/docs/pre-research/SaveData.t260g.bin.json
```

## Pages

| Page | What it answers |
|---|---|
| [Overview](references/overview.md) | Build identity, save-tool scope, the three data layers, terminology |
| [World](references/world.md) | Room vs area vs previous map, table gaps, fixture movement |
| [Systems](references/systems.md) | Party, flags, shops, INIT, Battle Rank, races, completion |
| [Data](references/data.md) | ID namespaces, name-table offsets, provenance, table inventory |
| [Harness](references/harness.md) | Save lab, raw DEFLATE, diff/assert, BepInEx/IL2CPP plan |
| [Edge cases](references/edge-cases.md) | Verified traps, failure signatures, do-not-guess list |
| [Variants](variants/differences.md) | English/Japanese assets, PS1 vs Remastered, build drift |

## Quick checks

- A loaded file starts with `0xED` or another compressed byte, not `{`. If it
  starts with `{`, it is already a JSON mirror.
- `saveDataList.length` is 59. Do not count the `saveDataJsonStr` marker; that
  is 61 because quick and auto are included.
- `pty.psnCnt` 1 with 41 `ply` records is normal. The roster is stored for
  every character in every save.
- An empty item is `{itemNo: 255, itemCnt: 0}`. An empty equipment attack slot
  is 65535; an empty equipment item slot is 255.
- A room id in `imfName` is `imfXXX`; `imf303` is 771, Chateau Aiguille.
- `mapwk.map_name` 26 is Chateau Aiguille, not a room name. `25` would be
  Baccarat.
- A `snroFlg` byte should be read as a state value first and as bits second.
  The exact-state rule wins, then each set single-bit entry.

## What not to put in this pack

Game binaries, save files, patched assets, guide text, manual scans, map
renders, or the full local gameinfo tree. Hashes, field maps, and derived
counts are fine. The pack's `sources/manifest.local.json` is gitignored and is
never installed or bundled.
