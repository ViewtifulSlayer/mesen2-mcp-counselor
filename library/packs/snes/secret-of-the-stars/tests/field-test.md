# Field test

## Target

| Field | Value |
|---|---|
| ROM | Tecmo Secret of the Stars (USA) |
| Size | 1,572,864 bytes |
| SHA-1 | `958a0a835e2e39f382cb37a99098a3cdd4812cf7` |
| Mapper | LoROM |
| Server | Mesen2 MCP 0.6.0 |
| Date | 2026-11-01 |

The pack was `draft` before this run. The run below verified the core probe
addresses and promoted it to `verified`; the separate rubric score is recorded
in `CERTIFICATION.md`.

## Procedure

1. Start Mesen2 MCP with the ROM and:
   `--mcp-lib-dir=<repo>/library/packs/snes/secret-of-the-stars/lua/lib`.
2. `get_rom_info`: confirm the SHA-1 and size.
3. Fresh boot: advance 900 frames, then send 220 pulses of A (2 frames held,
   18 frames released). The title screen is reached at frame 5301.
4. Press START and wait 240 frames, then A and wait 40, then START and wait
   300 frames. The name-entry screen is reached at frame 5893.
5. At name entry, press UP, RIGHT, and A, then wait 300 frames. Ray's House is
   reached at frame 6265.
6. Run `probe-map` and `read-state`. Record the map id, encounter id, battle
   flag, game state, party slots, battle pools, and hero 0 name, rank, stats,
   and spells.
7. Cross-check `$0026` with the local full map-id table (`Map ID's.html`). The
   starter CSV only carries ids `00`-`13`, so it does not reach Ray's House.
8. For a battle, load the local level-25 Brasca save through the game's
   Continue menu. The save is a verification artifact, not pack content. This
   build has no battery-load tool, so the harness wrote the 8 KB `.srm` bytes
   to `snesSaveRam`, power-cycled, and selected Continue, file 1.
9. Run `probe-map` and `read-state` in Brasca, then walk the world map until
   `battleFlag=5`. Wait 300 frames for the active battle.
10. Finish the battle with A presses. Record the victory state and the return
    to the field.
11. If a JP ROM is available, repeat steps 2-6 on Aqutallion and compare the
    map id and item names. Do not assume the US addresses apply. This was not
    run in this pass.
12. From the Brasca save, walk the south-entrance workaround, then the north
    edge and House 2. Record `$00B8` and `$00BB`.
13. Approach the Ancient Well ring in the north-east clearing from every
    reachable side. Record whether `$040E` changes. Do not record `$0146` as
    a walked gate unless it does.
14. Load the world-map cave state and walk `$00C0` to its end. Record whether
    the map has an exit.

## Recorded result

### Fresh boot

| Field | Value |
|---|---|
| Title frame | 5301 |
| Name entry frame | 5893 |
| Ray's House frame | 6265 |
| `mapId` | `$0026` (Ray's House) |
| `encounterId` | `$00` |
| `battleFlag` / `gameState` | `01` / `00` |
| Aqutallion slots | `[00, FF, FF, FF, FF]` |
| Kustera slots | `[FF, FF, FF, FF, FF]` |
| Kustera size | `00` |
| Battle gold / EP | `0` / `0` |
| Hero 0 | name `A`, rank `00`, level `01`, HP `32/32`, MP `0/0`, power `18`, defense `17`, speed `5`, luck `8`, condition `$00` |

The status screen independently showed `A 32/32 0/0 1` and the same HP, MP,
and level as the hero block. Local screenshot: `sots-060-house.png`.

### Brasca continue

| Field | Value |
|---|---|
| `mapId` | `$00B8` (Brasca) |
| `encounterId` | `$00` |
| `battleFlag` / `gameState` | `01` / `00` |
| Aqutallion slots | `[00, 02, 01, 03, FF]` = Ray, Cody, Tina, Leona |
| Kustera slots | `[05, 06, 07, 08, 09]` = David, Ryu, Ben, Andy, Arthur |
| Kustera size | `05` |
| Battle gold / EP | `0` / `0` |
| Hero 0 | name SABIN, rank `01`, level `25`, HP `180/180`, MP `93/93`, power `97`, defense `110`, speed `70`, luck `91`, condition `$00` |

The battle screen showed SABIN, CODY, TINA, LEONA in that order. Local
screenshot: `sots-060-brasca.png`.

### Brasca route beyond the entrance

From the level-25 Continue save (file 1, south entrance, `$00B8`, frame 1896):

| Gate | Input observed | `mapId` after | Evidence |
|---|---|---|---|
| South entrance to interior | right 70, down 30, right 70, up 60, then up 60 | `$00B8` | `sots-brasca-east.png`, `sots-brasca-north.png` |
| North edge to House 2 | left 120, up 120 | `$00BB` | `sots-brasca-house2.png` |
| World-map cave to Sealed Cave | left 30, up 60 from `sots-cave-up2` | `$00C0` | `sots-c0-enter.png` |
| `$00C0` corridor to its end | up 20 tiles | `$00C0`; one-tile platform in the void, no exit | `c0-north.png` |

The first upward step from the south entrance is blocked by the sign and tree
line. The right/down/right/up sequence is a working way around it; the map id
remains `$00B8` throughout that approach. The House 2 row is a real map
transition read through `$040E`.

### Ancient Well approach (second run)

The ring is drawn at the top of the north-east clearing
(`sots-brasca-north2.png`, `well-b1.png`). This run tested the ring directly
instead of only walking past it.

| Probe | Input observed | Result |
|---|---|---|
| Step up from the ledge below the ring | up, three attempts | blocked; X/Y unchanged at `(1024, 304)` |
| Step right toward the ring's column | right, three attempts | blocked; X/Y unchanged at `(1040, 320)` |
| Flood walk of the north-east quarter | 154 distinct tile positions, four directions each | no `$040E` change anywhere; no `$0146` |
| Local door table | `Exit Doors.csv`, all rows into `$00BC` | source is `$80` (overworld) on every row; no row from `$00B8` |

The hedge above the ledge and the forest on the east edge meet with no walkable
gap. The ring itself was never stood on. The well is **located and approached,
not entered**; `$0146` stays a table id.

### Sealed Cave correction

`$00C0` was reached from the world-map cave in the earlier run and was written
up as the Sealed Cave. This run walked it out: the map is a dirt corridor that
runs north and ends on a single tile surrounded by black (`c0-north.png`).
There is no exit and no link to `$0146`. The map id is real, but the stage was
overstated; it is not evidence that the well dungeon was walked.

### First random battle

| Point | `battleFlag` | `gameState` | `mapId` | `encounterId` | Battle gold | Battle EP |
|---|---|---|---|---|---|---|
| Transition | `05` | `02` | `0000` | `79` | `0` | `0` |
| Active battle | `05` | `03` | `0000` | `79` | `0` | `0` |
| Victory | `05` | `04` | `0000` | `79` | `252` | `240` |
| Return to field | `01` | `00` | `0000` | `79` | `252` | `240` |

The pool rose by `84` gold and `80` EP per enemy defeated. The encounter id
kept `79` after the return to the field; it is not cleared and is not a battle
gate. Local screenshots: `sots-060-battle-active.png`,
`sots-060-victory.png`, and `sots-060-afterbattle.png`.

### Address verification

| Address | Result |
|---|---|
| `$0020` | battle flag `01` field, `05` entering/battle/victory |
| `$0053` | game state `00` field, `02` entering, `03` battle, `04` victory |
| `$040E` | 16-bit map id `$0026` Ray's House, `$00B8` Brasca, `$00BB` Brasca House 2, `$00C0` Sealed Cave (stub corridor) |
| `$02AC`-`$02AF` | player X and Y, big-endian, 16 units per tile; `(1040,320)` then `(1040,336)` after one step down; blocked steps leave it unchanged |
| `$043C` | encounter `$00` in the house, `$79` at battle, `$79` on field after |
| `$04A4`-`$04A8` | party positions with character ids and `FF` empty |
| `$04A9`-`$04AD` | Kustera positions, all five occupied at Brasca |
| `$04AE` | `00` before recruitment, `E0` with five Kustera members |
| `$04BD` | Kustera size `00` before, `05` at Brasca |
| `$0D1F` / `$0D21` | battle pools, not total gold; `0` on field, `252`/`240` after victory |
| `$5000` | 16 hero records at stride `$36`; name `A` at Ray's House and `SABIN` at Brasca; all 16 names found from SABIN to BETH at Brasca |
| `$5007` | rank tier `00` Ray L1, `01` Ray/Tina/Cody/Leona at Brasca, `04` Dan |

## Corrections from the run

- **Hero stride.** The draft said not to assume a stride. The 16 records are
  `$36` bytes apart, and BETH starts at `$532A`, ending the table at `$5360`.
- **Spell slots.** The hero block has seven spell bytes at `+$26`-`+$2C`, not
  five. The draft stopped at `+$2A`.
- **Class byte is a rank tier.** At Brasca, Ray, Tina, Cody, and Leona all read
  `01` (Pennon), and Dan read `04`. The byte at `+$07` is not the job label in
  `characters.csv`; the local notes' `00`-`03` list is incomplete, and `04` is
  not named there.
- **Encounter id.** `$043C` keeps the last encounter after the battle. The
  draft's field check could be read as "nonzero means battle"; that is wrong.
- **Battle pools.** `$0D1F` and `$0D21` are not the save's total gold. On the
  field in Brasca they read `0` with a rich save. The kit now calls them
  `battleGold` and `battleEp`; `gold` and `ep` remain aliases.
- **Kustera flags.** `$04AE` read `E0`, not the `2X`/`4X` pair alone. The byte
  is a flag mask; the two documented bits are not the whole mask.
- **Map id failure signature.** "Below `$100`" is not evidence of a one-byte
  read; many valid maps are below `$100`. The real failure is a map above
  `$FF` read as one byte.

## Artifacts

Local, gitignored, not part of the pack:

- `dist/field-test-0.6.0/results/sots-house-0.6.0.mss` (frame 6265)
- `dist/field-test-0.6.0/results/sots-brasca-0.6.0.mss` (frame 1896)
- `dist/field-test-0.6.0/results/sots-battle-0.6.0.mss` (transition)
- `dist/field-test-0.6.0/results/sots-battle-active-0.6.0.mss` (frame 2437)
- `dist/field-test-0.6.0/results/sots-victory-0.6.0.mss`
- `dist/field-test-0.6.0/results/sots-afterbattle-0.6.0.mss`
- `dist/field-test-0.6.0/results/sots-brasca-east.mss` (entrance workaround)
- `dist/field-test-0.6.0/results/sots-brasca-north.mss` (Brasca north edge)
- `dist/field-test-0.6.0/results/sots-brasca-house2.mss` (`$00BB`)
- `dist/field-test-0.6.0/results/sots-c0-enter.mss` (`$00C0`)
- `dist/field-test-0.6.0/results/sots-brasca-gap5.png` (well ring visible)
- `dist/field-test-0.6.0/results/sots-brasca-north2.png` (well ring visible)
- `dist/field-test-0.6.0/results/well-b1.png` (ledge below the ring)
- `dist/field-test-0.6.0/results/wellbfs-nodes/` (154 flood-walk states)
- `dist/field-test-0.6.0/results/c0-north.png` (`$00C0` void platform)

## Limitations

- The JP release was not run. The JP/US address assumption is still unverified.
- Ray's House, Brasca, and Brasca House 2 were reached. The Ancient Well was
  located and approached from every reachable side but not entered; `$0146`
  is a table id, not a walked gate. `$00C0` is a stub corridor, not a stage.
  The rest of the route remains an outline.
- `$02AC` is page-local. Coordinates jump when the party crosses a screen edge,
  so the flood walk proves walls and map ids, not a global path.
- `$02AC`-`$02AF` responds to movement, but its packing is not decoded.
- The remaining rows in `references/harness.md` under "Still unverified" were
  not exercised.

## Failure signatures

- `battleFlag=05` with `gameState=02`: entering a battle, not a frozen field.
- `battleFlag=05` with `gameState=04`: victory screen; A returns to the field.
- A nonzero `encounterId` on the field: the last encounter, not an active one.
- Battle gold/EP `0` on the field: expected; these are battle pools.
- `aqutallion` and `kustera` share values: the probe mixed the two ranges.
- A slot is `FF`: empty slot, not party member zero.
- Map id above `$FF` read as one byte: read `$040E` and `$040F` together.
- Hero 0 HP does not match the status screen: check the `$36` stride and the
  little-endian pair before suspecting the base.
- `attempt to index a nil value (global 'sots')`: the recipe header says
  `-- requires:` instead of `-- includes:`.
