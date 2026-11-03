---
title: "World and location model"
summary: "How the save names a place: room vs area vs previous map, the 69-area table, 869 room IDs, and the fixture movement."
coverage: partial
---

# World and location model

This page is not a route. It explains the four location-like fields in the save
and why only one of them is the current room.

## The four fields

| Field | Type | What it actually is | Evidence |
|---|---|---|---|
| `mapwk.imfName` | string | **Current room** asset, e.g. `imf303` | fixture |
| `mapwk.Value4` | number | Duplicate of the current room ID | fixture |
| `eventwk.mapNo` | number | **Previous** map ID | fixture |
| `mapwk.map_name` | number | 0-based index into the 69-area table | fixture |
| `saveItemInfoData.MapNumber` | number | Same area index, metadata copy | fixture |

The first three look like a location. The fixture separates them.

## Fixture evidence

The Asellus save holds three snapshots from one playthrough:

| Snapshot | Play time | `imfName` | `Value4` | `eventwk.mapNo` | `map_name` | `MapNumber` |
|---|---:|---|---:|---:|---:|---:|
| quick | 0h 2m | `imf1a9` = 425 | 425 | 132 | 26 | 26 |
| auto | 0h 8m | `imf303` = 771 | 771 | 425 | 26 | 26 |
| slot 0 | 0h 11m | `imf303` = 771 | 771 | 425 | 26 | 26 |

`imfName` moves 425 -> 771. `eventwk.mapNo` follows one step behind: it holds
132 before the quick save, then 425 after the player reached 771. `map_name`
and `MapNumber` stay at 26 while the room changes. `[V]`

That is why `imfName` is the current room and `mapNo` is the previous map. The
second save confirms it: T260G moves through rooms 12, 13, 85, and 221 while
`map_name` stays 3, Scrap. `[V]`

## Room IDs

Room IDs are global and interleaved across areas. `imf303` is 0x303 = 771,
"Chateau Aiguille, round room with coffins and flashing crystals". `0x055` is
85, "Scrap, Junk Shop" in the IMF list. The community room table called 0x055
"Shrike, junk shop"; the area field (3 = Scrap) settles that in the IMF list's
favour. The correction is recorded in `map_names.json`. `[V]`

The community room table has **869 IDs over 22-1209** and **319 gaps**:
`[236]`, `[425]`, `[891-1071]`, `[1073-1208]`. Those are source gaps, not a
parser fault. Room 425 is exactly the quick save's `imfName`, so an unnamed room
must render as a raw ID plus "not in the map table", not as a guessed name.
`[V]` `[D]`

## Area IDs

`mapwk.map_name` and slot `MapNumber` index a **69-record, 20-byte area table**
at offset 7,782,118 in `resources.assets`. The block ends at 7,783,498, exactly
where the 16-byte character table begins. The table is 0-based; 26 is Chateau
Aiguille, 25 is Baccarat, 5 is Koorong, 68 is Facinaturu Floor. `[V]` `[D]`

The area is the zone, not the room. It is the natural value for a load-screen
or save-slot label. It cannot be converted to a room ID arithmetically: rooms
are global and interleaved, and the Chateau's rooms span 426-849 plus 771 while
425 is a gap. `[V]`

## What is not known

- **Current area vs scenario start area.** Both fixtures stay inside their
  starting area, so the two readings coincide. A save made after leaving the
  start area is needed. The distinguishing test: T260G in Shrike predicts 16
  for current-area and 3 for scenario-start. `[U]`
- **`mapwk.obj[]`.** A fixed 64-entry array with `obj_cnt` live entries. The
  struct fields are not decoded. `[U]`
- **`eventwk.region`, `region_no`, `region_sound`.** Readable, not mapped to a
  region table. `[U]`

## How to probe

1. Load two snapshots from the same slot or the same file.
2. Read `mapwk.imfName`, `mapwk.Value4`, `eventwk.mapNo`, and
   `mapwk.map_name`.
3. Resolve `imfName` against `docs/map_names.json` and `map_name` against
   `constants.json.areas`.
4. If the name is missing, report the raw ID and the gap, not a nearby name.
5. To test the area question, save after crossing a zone boundary and compare
   `map_name` before and after.

The live version of this is a runtime read of `imfName` plus player position,
not a save diff. The bridge plan is in `harness.md`.

## Sources

- `[S:sfr-save-tool]` for the fixture evidence, the 69-area table, the room
  table, the 0x055 correction, and the gap list.
- `[S:sf-data-project]` for the PS1 room vocabulary that the IMF names follow.
- Local: `docs/save_layout.md` sections 4.6-4.8 and 8; `docs/map_names.json`;
  `docs/constants.json`; `docs/gameinfo/json/maps.json`.
