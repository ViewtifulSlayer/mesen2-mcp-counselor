---
title: "Edge cases and traps"
summary: "The traps that produce plausible but wrong values, the failure signatures, and the fields that must stay unmapped."
coverage: verified
---

# Edge cases and traps

Most save-tool bugs are not parser crashes. They are plausible values from the
wrong field. This page is the list of those.

## Traps that have already cost time

| Trap | Wrong reading | Correct reading |
|---|---|---|
| Location | `eventwk.mapNo` is the current room | It is the **previous** map; `imfName` is current |
| Area | `mapwk.map_name` / `MapNumber` is a room ID | It is a 0-based area index |
| Battle Rank | `sfSys.parLev` is the last-clear rank | It is the new-scenario starting rank |
| Party level | `pty.parLev` is the party level | The path does not exist; use `pty.each.parLev` |
| Learned arts | `getskill` is LSB-first | It is MSB-first: `(byte - 0x38) * 8 + bit` |
| Quick/auto | They mirror the active slot | They are independent snapshots |
| Current HP | `hpMax` is current HP | The save stores max only; no current-HP field |
| Party | `ply` presence means membership | `ply` is the full roster; use `psnCnt`/`team` |
| NG+ | `IsTakeover` is a completion flag | It is the carry-over (crown) marker |
| Fuse | `totalFuseRootStart[4]` is labelled | Index 4 is inferred Asellus; other routes unnamed |
| Monster form | `hpMax` is max in form | It is the form's base HP; add Prime HP |
| Mystic absorbs | Absorbs are in `eqpAtk` | They are in `tribial_work.data[4..12]` |
| Mystic arts | The arts are at `eqpAtk[5..7]` | They are at `eqpAtk[4..6]` |
| Mec stats | `ply` stats are effective totals | They are base; add `eqpItm` parts |
| Shop names | The game has shop names | It has none; labels are location + stock |
| Map 425 | 425 is a shifted ID | It is a gap in the source room table |
| Character 64 | It should resolve | It has no name-table entry; leave it unmapped |
| Integrity | `chk*` can be recomputed | No algorithm; do not touch it |
| Recompression | A recompressed file is equivalent | It is format-valid but not byte-identical |

## Failure signatures

- **A room name is wrong but the ID looks valid.** Check which field produced
  it. `map_name` 26 is Chateau Aiguille; a room table lookup on 26 can produce
  "Koorong, small sewer".
- **A fresh save reads a plausible party level.** `pty.parLev` is a phantom.
  The live value is `pty.each.parLev`, and it is a packed byte, not a level.
- **A flag byte expands to a dozen meanings.** Read the exact state value
  first. `snroFlg[0x55] = 0xEC` is five events, not eight separate booleans.
- **A monster's max HP is short by 12.** Add Prime HP: 4 per distinct absorbed
  ability in ids 128-255. Riki is 60 base + 12 Prime = 72.
- **A Mec's stats look too low.** The record is base + parts. T260G is 100 base
  + 110 parts = 210 HP.
- **A Mystic panel shows three empty rows.** The arts are at `eqpAtk[4..6]`;
  the absorbs are at `tribial_work.data[4..12]`. An empty absorb is
  255/0/0, not a missing field.
- **A shop table reads complete but the achievement is not earned.** The ledger
  counts per table, not per distinct item, and 18 items are stocked by more
  than one table.
- **A slot picker shows 61 but the list is 59.** The marker count includes
  quick and auto. Use `saveDataList.length`.
- **A byte dump is off after an edit.** Marker offsets shift. Never use them as
  identifiers.
- **A save passes a round-trip but the game rejects it.** Format-valid is not
  integrity-valid. The write path is disabled for a reason.

## Do not guess these

| Area | Why it is blocked | Next test |
|---|---|---|
| `sfSys.chk*`, `sum`, `pty.sum` | No algorithm | Hook the save write |
| `getType` (0x17) | No glossary; 0-11 seen | Controlled save diffs |
| `mPart` | 240 on all but one record | Controlled save diffs |
| `tribial_work` remaining bytes | Only Mec/Monster/Mystic subsets mapped | Progression diffs |
| `boxFlg` | All zero in slot 0 | Trigger events |
| `eventwk.wk` | Sparse, no mapping | Trigger events |
| `eventwk.temp` except 192 | Only 192 mapped | Trigger events |
| `snroFlg` 343 bytes | No dictionary | Extend the source or hook writes |
| `mapwk.obj[]` | Struct array undecoded | Compare maps |
| Current vs start area | Fixtures do not cross areas | Post-area-change save |
| INIT 3 | No BR 4-6 clear | Controlled clear |
| Last-clear rank | Not `sfSys.parLev` | Hook the save write |
| Fuse routes 0-3, 5-7 | One fixture | Second route fixture |
| `chrNo` 0x40 | No name-table entry | Asset search or live inspection |

## Integrity and recompression

The real 16,933-byte file inflates to 254,131 bytes. Recompression was measured
across 3,150 combinations of zlib level 0-9, memLevel 1-9, strategy (default,
filtered, huffman-only, rle, fixed), and windowBits 9-15, plus both rotation
backups. None reproduces the container byte for byte. The best zlib output is
15,669 bytes, 1,264 bytes smaller than the game's 16,933. That is consistent
with a chunked writer emitting flush points, not a different codec. `[V]`

Consequence: a byte-equality test is not proof of correctness, and a
format-valid edit is not proof that the game will accept it. Do not add a save
download, an editor, or a checksum "fix" until the four `chk*` fields and `sum`
are understood.

## Version and asset traps

- The English and Japanese `BaccaratTblData.bin` copies are both in
  `resources.assets`, at Path IDs 1234 and 574. Selecting the wrong one changes
  the table you read. `[S:ffvd-baccarat-skills]`
- The name tables are asset-sourced; the ability, flag, INIT, item-stat,
  monster, mystic, and shop tables are community-sourced. Do not label the
  latter as game text.
- The PS1 documents are corroboration, not authority. The Remastered asset
  table wins on spelling: `AGUNI-CP1`, `T260`, `GoldIngot`.
- Build hashes pin the install. A Steam update can change `GameAssembly.dll`,
  `resources.assets`, and the metadata together; re-measure before trusting an
  offset.
- The localization restoration mod notes an ASCII/SHIFT_JIS conversion routine
  that can hard-freeze on mixed text. This is not a save-tool issue, but it is
  a reason not to feed arbitrary text into the game while testing. `[S:ffvd-sfr-modding]`

## When a value disagrees with the guide

1. Check whether the source is PS1 or Remastered.
2. Check whether the field is asset-sourced or community-sourced.
3. Check whether the value is a base value or a computed total.
4. Check whether the fixture is a controlled save or a natural one.
5. If the disagreement remains, record both values and mark the field
   ambiguous. Do not silently pick one.

## Sources

- `[S:sfr-save-tool]` for every verified trap and the recompression measurement.
- `[S:sf-data-project]` for the PS1 mechanics and the INIT/Monster/Mystic rules.
- `[S:ffvd-baccarat-skills]` and `[S:ffvd-sfr-modding]` for the asset copies
  and the localization freeze.
- Local: `docs/save_layout.md` section 11; `docs/project_runbook.md` sections
  4-7; `docs/agent_state.json`.
