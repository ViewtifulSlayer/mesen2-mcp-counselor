---
title: Mesen harness
summary: Verified 0.6.0 RAM addresses, the player coordinate pair, the 0x36 hero block, party probes, battle pools, and the remaining unverified notes.
coverage: verified
---

# Mesen harness

Tags follow `SKILL.md`: `[V]` field-tested, `[D]` documented, `[U]` unverified.

The verified table was checked on Mesen2 MCP 0.6.0 against the USA ROM
(`958a0a835e2e39f382cb37a99098a3cdd4812cf7`) on 2026-11-01. `[V]` The run booted
a new game to Ray's House, then loaded a local level-25 Brasca save through the
game's Continue menu and fought one random battle. `[V]` Exact values are in
`tests/field-test.md`.

The local Landmine36 `RAM Notes` remain the source for the unverified rows at
the bottom `[D]`. Do not present those as field-tested `[U]`.

## Verified address map

Every row in this table is `[V]` on the USA ROM.

| Address | Width | Meaning | Observed on 0.6.0 |
|---|---|---|---|
| `$0020` | 8 | battle flag | `01` on the field; `05` entering battle, in battle, and on the victory screen |
| `$0053` | 8 | game state | `00` field, `02` entering battle, `03` battle, `04` victory |
| `$040E` | 16 | map id | `$0026` Ray's House, `$00B8` Brasca; little-endian |
| `$043C` | 8 | encounter id | `00` in Ray's House, `79` at the battle; keeps `79` after returning to the field |
| `$04A4`-`$04A8` | 8 each | Aqutallion party slots 1-5 | `[00,FF,FF,FF,FF]` at Ray's House; `[00,02,01,03,FF]` at Brasca |
| `$04A9`-`$04AD` | 8 each | Kustera party slots 1-5 | `[FF,FF,FF,FF,FF]` at Ray's House; `[05,06,07,08,09]` at Brasca |
| `$04AE` | 8 | Kustera recruit flags | `00` before recruitment; `E0` with the five-member Brasca party |
| `$04BD` | 8 | Kustera party size | `00` at Ray's House, `05` at Brasca |
| `$0D1F` | 16 | battle gold pool | `0` on the field; `84`, `168`, `252` as enemies fell; `252` remained after victory |
| `$0D21` | 16 | battle EP pool | `0` on the field; `80`, `160`, `240` as enemies fell; `240` remained after victory |
| `$5000` | 16 blocks | hero records | 16 records, stride `$36`; block `n` is at `$5000 + n * $36` |

### Party slots

The five bytes at `$04A4` and the five at `$04A9` are party positions, not a
combined roster. `[V]` Each value is a character id: `00` Ray, `01` Tina, `02`
Cody, `03` Leona, `04` Dan, `05` David, `06` Ryu, `07` Ben, `08` Andy, `09`
Arthur, `0A` Evelyn, `0B` Jubei, `0C` Murray, `0D` Shark, `0E` Kathy, `0F` Beth.
`FF` is an empty slot. `[V]`

At Brasca the Aqutallion bytes were `00 02 01 03 FF` (Ray, Cody, Tina, Leona)
and the battle screen showed SABIN, CODY, TINA, LEONA in that order. The
Kustera bytes were `05 06 07 08 09` and the party size was `05`. `[V]`

`$04AE` is a flag byte, not a count. It read `00` before recruitment and `E0`
with all five Kustera members. `[V]` The local notes identify `2X` as David and
`4X` as Ryu `[D]`; the remaining bits were not isolated `[U]`.

### Map and encounter

`$040E` is a 16-bit little-endian value. Reading only the low byte is correct
for maps below `$100` and wrong for maps above it. `[V]` Both tested maps are
below `$100` (`$0026` and `$00B8`), but the high byte at `$040F` must still be
read. `[V]`

`$043C` is the current or most recent encounter id. It read `00` in Ray's
House, `79` at the random battle, and still `79` after the party returned to
the field. `[V]` Do not use it as a battle gate; use `$0020` and `$0053`. `[V]`

### Player coordinates

`$02AC`-`$02AF` is the player coordinate. `[V]` X is the big-endian pair at
`$02AC`-`$02AD`; Y is the big-endian pair at `$02AE`-`$02AF`. One tile is 16
units, so a step right adds `16` to X and a step down adds `16` to Y. `[V]`

| Read | X | Y |
|---|---|---|
| Brasca, before a step | `1040` | `320` |
| one tile down | `1040` | `336` |
| one tile right | `1056` | `320` |
| blocked step against the hedge | unchanged | unchanged |

The pair is **camera-page local, not a global map position**. `[V]` Crossing a
screen boundary of the same map changes the high byte with no walkable link:
at the north-east corner of Brasca, `(1024, 304)` stepped left and read
`(1264, 48)`, and stepping right read `(1024, 304)` again. `$040E` stayed
`$00B8` throughout. Use the pair to tell whether a step moved, not to address a
tile on the ROM's map.

Writing the four bytes relocates the party and the camera follows within about
30 frames `[V]`. That is a harness tool for placing the party at a known tile,
not a game mechanic; say so in any test that uses it.

```lua
-- run_recipe includes=["sots_kit"]
local function be16(address)
  return 256 * sots.r8(address) + sots.r8(address + 1)
end
local x, y = be16(0x02AC), be16(0x02AE)
emu.log(string.format("player x=%d y=%d tile=%d,%d", x, y,
  math.floor(x / 16), math.floor(y / 16)))
```

### Hero records

The hero table holds all 16 characters in id order, starting at `$5000`. The
stride is `$36` (54 bytes), verified by walking the 16 names from SABIN at
`$5000` through BETH at `$532A`. `[V]`

| Offset | Meaning | Notes | Evidence |
|---|---|---|---|
| `+$00`-`+$06` | name | letters are `40` + ASCII; `FF` terminates; the seventh byte is unused | `[V]` for the encoding and terminator; `[D]` for the unused seventh byte |
| `+$07` | class/rank tier | `00` none, `01` Pennon (Ray, Tina, Cody, Leona), and `04` (Dan) observed; `02` Banalet and `03` Aqutalion come from the local notes | `[V]` for `00`/`01`/`04`; `[D]` for `02`/`03`; `[U]` for the `04` label |
| `+$08` | level | `01` and `25` observed | `[V]` |
| `+$09`-`+$0B` | EXP, low to high | values not interpreted | `[U]` |
| `+$0C`-`+$0E` | EXP to next level | values not interpreted | `[U]` |
| `+$0F`-`+$10` | current HP | little-endian | `[V]` |
| `+$11`-`+$12` | total HP | little-endian | `[V]` |
| `+$13`-`+$14` | current MP | little-endian | `[V]` |
| `+$15`-`+$16` | total MP | little-endian | `[V]` |
| `+$17`-`+$18` | power | little-endian | `[V]` |
| `+$19`-`+$1A` | defense | little-endian | `[V]` |
| `+$1B`-`+$1C` | speed | little-endian | `[V]` |
| `+$1D`-`+$1E` | luck | little-endian | `[V]` |
| `+$1F` | condition bits | all tests read `00`; bit meanings remain local-note claims | `[V]` for the zero reads; `[D]` for the labels; `[U]` for the meanings |
| `+$20` | lion sprite | not exercised | `[U]` |
| `+$22`-`+$25` | weapon, armor, helm, shoes | offsets verified; item ids not decoded | `[V]` offsets; `[U]` item ids |
| `+$26`-`+$2C` | seven spell slots | seven bytes verified, not five; spell ids not decoded | `[V]` bytes; `[U]` spell ids |
| `+$2D`-`+$35` | unknown | nine trailing bytes; do not write | `[U]` |

Hero 0 at Ray's House read name `A`, rank `00`, level `01`, HP `32/32`, MP
`0/0`, power `18`, defense `17`, speed `5`, luck `8`, condition `00`. Hero 0 at
Brasca read name `SABIN`, rank `01`, level `25`, HP `180/180`, MP `93/93`,
power `97`, defense `110`, speed `70`, luck `91`, condition `00`. Both matched
the status and battle screens. `[V]`

### Battle pools

`$0D1F` and `$0D21` are the gold and EP pools used during a battle. They are
not the save's total gold. On the field in Brasca they read `0` even though the
save had money. In the first battle they rose by `84` gold and `80` EP per
enemy defeated, reaching `252` and `240` on victory, and kept those values
after the return to the field. `[V]`

## Observed but not decoded

The raw observations in this section are `[V]`; the interpretation of every
row is `[U]`. These changed in the field test, but the layout is not established
enough to use as a menu API.

| Address | Observation |
|---|---|
| `$02AC`-`$02AF` | now decoded as the player coordinate; see "Player coordinates" above |
| `$04B0`, `$04B2` | read `8000` and `0080` while the field menu was open. These match the notes' B and A bits, but the values latch after release. They are an input mirror, not a cursor. |
| `$04B4`, `$04B5` | present in the notes; not exercised in the 0.6.0 run. |

## Still unverified

These remain local-note claims `[D]`; treat them as `[U]` for live use. Keep
them out of a patch until a focused run tests them.

- `$0411` name entry (48 bits)
- `$0434` event id (16 bits)
- `$04B6` party controlled, `$04B7` repel counter, `$04B8` step spell
- `$0529` battle background id
- `$097A` BGM id
- `$0A57` / `$0A58` active action
- `$0A9F` / `$0AA0` Unity leader and participants
- `$5007` class/rank values `02` and `03`, and the name of `04`
- `$501F` condition bit meanings
- `$5022`-`$5025` equipment id meanings
- `$5026`-`$502C` spell id meanings

## Lua kit

The kit reads through `snesWorkRam` and was exercised against both saved states
on 0.6.0. `[V]`

```lua
-- run_recipe includes=["sots_kit"]
local state = sots.state()
emu.log(sots.describe(state))
```

`sots.state()` returns the battle flag, game state, map id, encounter id,
Aqutallion and Kustera slots, Kustera size, battle gold and EP pools, and the
hero 0 summary. `[V]` `sots.hero(index, offset)` reads a byte from any hero
record; `sots.heroName(index)` decodes the seven-byte name; `sots.spells(index)`
returns the seven spell bytes; `sots.heroSummary(index)` returns the name, rank,
stats, condition, and spell table. `[V]` `class` remains an alias for `rank`.
`sots.gold()` and `sots.ep()` remain aliases for the battle pools.

## Probe discipline

- Check the battle flag and game state together. One without the other can be
  stale during a transition.
- Read map id as 16-bit and encounter id as 8-bit.
- Keep Aqutallion and Kustera slots separate; both use `FF` for empty.
- Treat a nonzero encounter id on the field as the last encounter, not an
  active battle.
- Treat battle gold and EP as pools. Do not read them as the party's money.
- Index hero records with the `0x36` stride; do not infer the stride from the
  name length.
- Check `$02AC` before and after a step to prove movement. An unchanged pair
  plus a blocked direction means a wall, not a dropped input.
- Do not convert `$02AC` to a world position. It is page-local and its high
  byte jumps at screen edges.
