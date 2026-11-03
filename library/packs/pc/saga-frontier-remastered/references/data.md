---
title: "Data and ID namespaces"
summary: "ID ranges, name-table offsets, asset vs community provenance, ability schools, and the 11 runtime tables."
coverage: verified
---

# Data and ID namespaces

## Namespaces at a glance

| Namespace | Key format | Range | Count | Status | Source |
|---|---|---|---:|---|---|
| Item | `0xNN` | 0x00-0xFF | 256 | asset | `resources.assets` item table |
| Character | `0xNN` | 0x00-0x3F | 64 | asset | `resources.assets` character table |
| Area | `0xNN` | 0x00-0x44 | 69 | asset | `resources.assets` area table |
| Ability | `0x000-0x1FF` | 0-511 | 512 | documented | `ability_names.json` |
| Map / room | `0x000-0x4B9` | 22-1209 | 869 | community | `maps.json`, IMF list |
| Enemy / form | `0x00-0xFF` | 0-255 | 256 | documented | `monster_forms.json` |
| Shop Type | decimal | 0-90 | 17 | documented | `shop_names.json` |
| Scenario / hero | `0-8` | 0-8 | 9 | documented | `SystemData.HERO` |
| Ending | `0-16` | 0-16 | 17 | documented | `SystemData.ENDING` |
| Element flag | code | 14 flags | 14 | documented | `ability_names.json` |
| INIT set | `1-4` | 1-4 | 4 | documented | `init_sets.json` |

The exact rows are in `data/id-namespaces.csv`.

## Name tables

The game's own item, character, and area names are fixed-width padded ASCII
tables in `resources.assets`:

| Table | Offset | Record width | Records |
|---|---:|---:|---:|
| Item | 7,738,252 | 16 bytes | 256 |
| Area | 7,782,118 | 20 bytes | 69 |
| Character | 7,783,498 | 16 bytes | 64 |

The area block ends exactly where the character table starts, which is why 69
records is the right count for 1,380 bytes. The extractor asserts printable
ASCII, space padding, and alignment before it writes anything. `[V]` `[D]`

Alignment evidence for the item table: index 7 Backpack (matches slot 0
`item_a[0]`), 17 BroadSword, 128 FiberVest, 169 SilkShirt, 192 LeatherBoots,
240 GoldIngot, 250 Magi-Water, 253 RegionMap. Character: 0 Emelia, 5 Asellus,
6 T260, 8 Rouge, 39 RedTurnip. Area: 5 Koorong, 26 Chateau Aiguille, 68
Facinaturu Floor. `[V]`

**The community table used earlier was wrong on many indices.** It placed
Broad Sword at 0x02, Zero Sword at 0x0A, and Gold Ingot at 0xFA; the game table
has BroadSword at 0x11, ZeroSword at 0x25, and GoldIngot at 0xF0. It also listed
a Katar that does not exist in the game table. Do not resurrect those values.
`[V]`

Character 0x40 appears as a real `ply` record but has no entry in the 64-record
name table. It stays unmapped. `[V]`

## Provenance status

`constants.json` uses five labels:

| Status | Meaning |
|---|---|
| `verified` | Confirmed by both the live save and the game name table |
| `asset` | Read from the game name table; authoritative in-game spelling |
| `documented` | Community table only; cross-checking, not display |
| `ambiguous` | Sources disagree; render with a warning |
| `unknown` | ID occurs but no reliable name |
| `placeholder` | Table entry exists but is marked NotUse |

`ability_names.json`, `flag_names.json`, `init_sets.json`, `item_stats.json`,
`monster_forms.json`, `monster_lab.json`, `mystic_absorbs.json`, and
`shop_names.json` are **documented** or **draft**, not asset-extracted. They
are useful, but they are not the game's own strings. `[V]` `[D]`

## Ability IDs

Ability IDs are 0-511. `getskill` is 64 bytes at 0x38-0x77; each byte holds
eight abilities, most significant bit first:
`ability_id = (byte - 0x38) * 8 + bit`. Slash is 0, ThunderThrust is 8, Defense
is 511. `[V]`

The 512 IDs split into eight schools:

| Byte range | Ability IDs | School | Basis |
|---|---|---|---|
| 0x38-0x3F | 0-63 | Sword | documented header |
| 0x40-0x41 | 64-79 | Gun | documented header |
| 0x42-0x47 | 80-127 | Fighting | documented header |
| 0x48-0x57 | 128-255 | Monster | inferred |
| 0x58-0x63 | 256-351 | Magic | documented header |
| 0x64-0x6D | 352-431 | Dodge / Mec | documented header |
| 0x6E-0x75 | 432-495 | Mystic / Enemy | documented header |
| 0x76-0x77 | 496-511 | Enemy | inferred |

The Monster block is exactly 128 slots, matching the 128 Monster abilities; no
Human, Mystic, or Mec INIT record holds one, while every Monster does. The enemy
block lies past the last PC category and no character in any INIT set or save
holds a bit in it; the entries enemies use are boss/AI actions. Both sections
carry a `basis` field so the inference is visible. `[V]` `[D]`

## Map IDs

The community room table has 869 IDs over 22-1209, with 319 gaps. The gaps are
in the source, not the parser. Room 0x303 is the same in the PS1 list and the
Remastered save, so there is no ID offset between the versions. `[V]` `[D]`

One correction is applied: 0x055 is "Scrap, Junk Shop", not "Shrike, junk
shop". The area field (3 = Scrap) and the IMF list agree. The correction record
keeps the old value and the reason. `[V]`

## Item stats

`item_stats.json` has 240 rows, 0x00-0xEF, from the Data Mechanics Guide's Mec
chart `[ITEMD03]`. It carries one HP field and the seven stat boosts, with
`null` where the guide prints a dash. It is **Mec only**. Human, Mystic, and
Monster records use different tables and must not read these values. Key items
0xF0-0xFF are not equippable and are omitted. `[D]`

## Monster data

`monster_forms.json` has 256 form IDs and 120 documented targets, backed by
144 requirement rows: 16 Table 1 rows for 13 targets, and 128 Table 2 rows for
107 targets across 74 forms. `monster_lab.json` has 134 ability entries (128
Monster plus six Space Magic Head) and 88 form-stat entries covering 86
documented Oulak blocks. Documented stats are shown beside the observed record,
never substituted for it. Two blocks (Ogre** and SuzakuJr.**)
carry no BHP line; Mandrake is documented at 110 BHP while the fixture stores
160. The library labels these rather than reconciling them. `[D]`

## Mystic data

`mystic_absorbs.json` has 256 enemy IDs and 465 art slots across 160 armed
enemies, from `[MYSAB02]`. Names and granted arts are the guide's extracted
data, not save fields. A stat missing from normal or variants means the guide
prints a dash, not zero. The save stores the resolved mask and amount, so the
viewer compares stored values with the normal row and each documented variant
instead of guessing which applied. `[D]`

## Shop labels

`shop_names.json` has 17 entries. Labels are location plus stock, not in-game
names, because the game has no shop-name table. A Type with no label falls back
to "Shop table N"; do not guess from where a purchase was made. The gold split
(14 Koorong, 90 Nelson) is medium confidence because both stock only
`GoldIngot`. `[D]` `[S:essence-of-saga]`

## Table inventory

`data/tables-inventory.csv` lists the 11 runtime tables and the seven gameinfo
source datasets, with record counts, generators, and status. The runtime tables
are the ones the viewer fetches; `docs/gameinfo/` is local research and must not
be deployed. `[V]`

## Rights and provenance

The name tables are short factual identifiers, not prose. The community tables
are facts and counts, re-expressed in the save tool's schema; no guide text is
copied. The pack ships no game files, saves, scans, or map renders. The local
manifest records source paths and hashes and is gitignored. `[V]`

## Sources

- `[S:sfr-save-tool]` for the name-table extraction, alignment checks, ID
  tables, and provenance labels.
- `[S:sf-data-project]` for the PS1 ability/stat/monster/mystic tables.
- `[S:ffvd-baccarat-skills]` for the English/Japanese asset copies.
- `[S:essence-of-saga]` for shop sale locations.
- Local: `docs/constants.json`, `docs/ability_names.json`, `docs/map_names.json`,
  `docs/item_stats.json`, `docs/monster_forms.json`, `docs/monster_lab.json`,
  `docs/mystic_absorbs.json`, `docs/shop_names.json`,
  `docs/gameinfo/json/manifest.json`.
