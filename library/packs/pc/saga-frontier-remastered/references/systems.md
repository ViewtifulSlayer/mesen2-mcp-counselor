---
title: "Systems stored in the save"
summary: "Party, roster, scenario flags, Battle Rank, INIT sets, shops, races, Mec/Mystic/Monster records, and completion state."
coverage: partial
---

# Systems stored in the save

## Party and roster

`pty` is the active party and the player state. `ply` is the full character
roster.

| Field | Length | Meaning |
|---|---:|---|
| `pty.psnCnt` | - | Active party count; 1 in the Asellus slot 0 |
| `pty.heroNo` | - | Leader character ID; 5 in slot 0 |
| `pty.chrNo` | 56 | Roster order, 255 padded |
| `pty.companionChrNo` | 56 | Companion list, 255 padded |
| `pty.team` | 56 | Active party order, 255 padded |
| `ply` | 41 | One record per character in every save |

`pty.chrNo`, `companionChrNo`, and `team` are 56 entries, not 41. The padding
is 255. With `psnCnt` 1, the four party fields agree on the leader in the
fixture; that is a strong observation, not an engine contract. `[V]`

**Presence in `ply` is not membership.** Slot 0 has 41 populated roster records
and a one-member party. Do not derive the party from `ply`. `[V]`

## Scenario order and completion

`SystemData.HERO` is the scenario order:

| Index | Scenario |
|---:|---|
| 0 | Emelia |
| 1 | Lute |
| 2 | Red |
| 3 | Fuse |
| 4 | Blue |
| 5 | Asellus |
| 6 | T260G / ROBO |
| 7 | Riki / COON |
| 8 | Rouge |

`systemData.clearFlag` is 16 entries, HERO-indexed; `systemData.endingFlag` is
17 entries, ENDING-indexed. The 2021 fixture has `clearFlag[3]` (Fuse) and
`clearFlag[5]` (Asellus), with `endingFlag[6]` (ASELLUS_HALF) and
`endingFlag[14]` (FUSE_ASELLUS). `[V]`

The Fuse group is per file, not per slot: `isFuseAppearance`,
`totalFuseBossNum[8]`, `totalFuseRootStart[8]`, `totalFuseRootClear[8]`. In the
2021 file, `totalFuseRootStart[4]` is 5 and `totalFuseRootClear[4]` is 2. Index
4 is inferred to be the Asellus route from the Fuse slot's
`RouteCharacterNumber` 5 and `endingFlag[14]`. The other seven route names are
not assigned. `[V]` `[U]`

`systemData.saveDataIndex` is the active slot index in `saveDataList`. It moved
from 5 to 10 between the 2021 and 2026 files. `[V]`

## Flags

`pty.snroFlg` is 512 bytes. It is **not** a boolean array:

- Some bytes are bit fields; one `0xFF` can expand to several meanings.
- Some bytes are counters. Index 0x0F is labelled `ランダム値` (random value);
  it holds 23 in the 2-minute snapshot and 101 in the 11-minute one.
- Index 0x00 is a calculation-area marker, not a flag.
- 169 bytes have names; 343 do not. `[V]` `[D]`

The match rule in `flag_names.json` is: an exact state value wins; otherwise
every single-bit entry whose bit is set; otherwise the byte is shown raw. That
rule reproduces all six fixture cross-checks, including `snroFlg[0x25] = 0xF0`
(Asellus + protagonist), `snroFlg[0x55] = 0xEC` (five early T260G events), and
`snroFlg[0x2A] = 0xF1` (Gen joined). `[V]`

`pty.scenarioChartStateArray` is a separate 1,024-byte array. Indices 157 and
158 match `asellus_00_00` and `asellus_00_01` in the local
`ScenarioChartDataTable`, but what a set value means is not known. `[V]` `[U]`

`pty.boxFlg` (64), `eventwk.wk` (32), and most of `eventwk.temp` (256) are not
mapped. `eventwk.temp[192]` is the per-slot additional-content mode: 1 on, 0
off, inferred from the clean slots 7/8 pair. `[U]`

## Battle Rank

`pty.each.parLev` is the live **packed Battle Rank Points byte**, not a level
and not a quarter-BR. The scale is 16 points per rank: the high nibble holds
BR-1, the low nibble the points toward the next rank. `[V]` `[D]`

| Value | Reading |
|---|---|
| `0x00` | BR 1, 0 points |
| `0x17` | BR 2, 7 points |
| `0x3F` | BR 4, 15 points |
| `0x85` | BR 9, 5 of 13 toward resetting to late BR 8 |

The INIT brackets are therefore `parLev` 0-47 (BR 1-3), 48-95 (BR 4-6), and
96-143 (BR 7-9). `[D]`

`sfSys.parLev` is a different field. It is the System Data's **new-scenario
starting rank**: 0 in both no-clear fixtures, 33 in the post-clear files, and
33 even on fresh post-clear slots at 1-3 minutes. It is not the active-slot
mirror, not the last-clear rank, and not the selector input. `[V]`

`pty.parLev` does not exist. If a viewer reads it, it renders a phantom dash.
The live value is `pty.each.parLev`. `[V]`

## INIT sets

Every scenario start rewrites HP, LP, WP, JP, the seven stats, starting
equipment, and the learned-art count from one of four fixed tables. The save
keeps the result, so the viewer can identify the set by comparing records.
`[V]` `[D]`

Selection rule: no completed scenario -> INIT 1; last clear at BR 1-3 -> INIT 2;
BR 4-6 -> INIT 3; BR 7-9 -> INIT 4. `[D]`

Observed: INIT 1 (Asellus, no prior clear), INIT 2 (Fuse, after Asellus at
BR 3), INIT 4 (Riki and both fresh Asellus starts, after Fuse at BR 9). **INIT 3
is not observed.** A BR 4-6 clear is the missing fixture. All 29 populated
snapshots across four fixtures match the documented branch with no
contradictions. `[V]` `[U]`

`docs/init_sets.json` holds 158 records across four sets: sets 1 and 2 cover all
40 INIT characters (`0x00-0x27`), while sets 3 and 4 cover 39 because `0x00` is
absent. The separate `chrNo` 0x40 roster record has no INIT entry in any set, so
a fresh save matches 40 of its 41 roster records with sets 1-2, and 39 of 41
with sets 3-4. `[V]`

## Races

`ply.race` is the Race/Gender byte at 0x16. `ply.nature` is the Gifts bitfield
at 0x15. `ply.getType` is byte 0x17 and is still undecoded. `[V]` `[U]`

| Race byte | Meaning |
|---|---|
| `0x41` | Human female |
| `0x81` | Human male |
| `0x42` | Mystic female |
| `0x82` | Mystic male |
| `0x04` | Mec |
| `0x08` | Monster |
| `0x98` | Monster with bits 4 and 7 also set |

Gifts: `0x80` Rune, `0x40` Arcane, `0x20` Evil, `0x10` Mind, `0x08` Mystic,
`0x04` Realm, `0x02` Shadow, `0x01` Light. `[D]`

### Mec

A Mec record holds the body's **base** values, not the effective totals. The
eight `eqpItm` slots hold the parts, and the game adds their boosts. T260G's
base HP is 100 and its parts add +110, for 210; the seven stats follow the same
base + parts rule. `tribial_work.data[0]` is the body TYPE index (0-7); the
record mirrors `hpMax` in `data[2]`. The Mec boost table is `item_stats.json`
(240 rows, 0x00-0xEF) and applies to Mec only. `[V]` `[D]`

### Mystic

The three Mystic weapon arts are `eqpAtk` entries, not the absorbs: `0x1B0`
MysticSword, `0x1C0` MysticGlove, `0x1D0` MysticBoots, at `eqpAtk[4..6]`.
The absorbed enemy is in `tribial_work.data[4..12]`, three enemy/mask/amount
triples in sword/glove/boots order: enemy 4/5/6, mask 7/8/9, amount 10/11/12.
The mask is one bit per stat in STR/QUI/INT/WIL/PSY/VIT/CHA order; the amount
applies to every masked stat. An empty weapon is enemy 255, mask 0, amount 0.
`[V]`

An earlier reading used `eqpAtk[5..7]`; that is wrong. The arts are at indices
4-6. Absorbs are never in `eqpAtk`. `[V]`

### Monster

A Monster record uses three parts for one form:

| Field | Meaning |
|---|---|
| `tribial_work.data[0]` | Current form ID, in the enemy namespace (0-255) |
| `hpMax` | The form's base HP |
| `getskill` ids 128-255 | Absorbed history; each distinct id adds 4 Prime HP |
| `eqpAtk[0..7]` | The live eight-slot ability menu; 65535 empty |

Prime HP is `4 x distinct absorbed monster abilities`; max in form is
`hpMax + Prime`. Riki's INIT 1 record is form 15, base 60, ids 165/166/173
(Tail/TailHit/Heal), so Prime 12 and max 72. `[V]`

The transformation check reads the equipped menu in the order **8, 1, 2, 3, 4,
5, 6, 7**, not 1-8. Table 1 requires every listed ability; a row for the
current form is skipped. If Table 1 has no match, Table 2 starts at the first
row whose `hp_below` ceiling is above the current max HP, walks forward to the
end, then wraps. Table 2 checks only the first ability in each of Head, Arm,
Leg, Body, Breath, and Magical. Space Magic is Head for that rule but cannot
satisfy a requirement. `[D]`

The save does **not** store a per-PC INIT ability table for Monsters.
`getskill` is the absorbed history and `eqpAtk` is the live menu. `[V]`

## Shops

`systemData.shopRecordList` is a purchase ledger, not a list of visited shops.
It has 17 fixed stock tables, each a `Type` with `ItemRecord[]` of
`{ItemID, PurchaseItemCount}`. The stock lists are identical in both project
saves, including the 11-minute one, so they are fixed game data copied into
every file; only the counts move. `[V]`

Across the 17 tables: 102 stock entries, 84 distinct items, 18 items stocked by
more than one table. T260G has bought 8 entries, all in table 5, which is 8 of
8; Asellus has bought nothing. The achievement is "Purchased all types of items
sold at shops" (Shopaholic), so the card reports both entries bought and
distinct items bought. `[V]` `[S:essence-of-saga]` `[S:steam-shopaholic]`

The game has no shop-name table: `global-metadata.dat` contains `ShopRecord`,
`ShopItemRecord`, and `ShopType`, but no shop name strings. `shop_names.json`
labels the 17 Type IDs by matching every item in each fixed stock list to its
documented sale location. That gives a location plus a stock description, not
an in-game name. The two gold tables (14 and 90) stock only `GoldIngot`; Koorong
and Nelson are the two documented gold sellers, so both are medium confidence.
`[V]` `[D]`

## Integrity fields

`sfSys.chk`, `sfSys.chk2`, `sfSys.chk3`, `sfSys.chk4`, `sfSys.sum`, and
`pty.sum` look checksum-like. No algorithm is known. Recompression was tested
against the real 16,933-byte file with 3,150 combinations of zlib level,
memLevel, strategy, and windowBits; none reproduces the container byte for
byte. The game's stream is 1,264 bytes larger than the best zlib output, which
is consistent with a chunked writer emitting flush points. `[V]`

Do not recompute, validate, or "fix" these fields. A format-valid edit is not
proof of a valid save. The write path is deliberately disabled pending this
question. `[V]`

## Sources

- `[S:sfr-save-tool]` for every fixture-verified field, the flag rule, INIT
  observation, shop ledger, and race records.
- `[S:sf-data-project]` for the PS1 mechanics, INIT tables, Mec/Mystic/Monster
  formulas, and Battle Rank packing.
- `[S:essence-of-saga]` and `[S:steam-shopaholic]` for shop sale locations and
  grouping.
- Local: `docs/save_layout.md`, `docs/project_runbook.md` sections 3-4,
  `docs/init_sets.json`, `docs/item_stats.json`, `docs/monster_forms.json`,
  `docs/monster_lab.json`, `docs/mystic_absorbs.json`, `docs/shop_names.json`.
