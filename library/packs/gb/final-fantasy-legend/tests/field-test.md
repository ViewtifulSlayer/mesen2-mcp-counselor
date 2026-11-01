# Field test

## Target

| Field | Value |
|---|---|
| ROM | Final Fantasy Legend, The (USA) |
| Size | 131,072 bytes |
| SHA-1 | `901dfc83c72e172d35a376835807fc788444a9bb` |
| Mapper | MBC2 |
| Measured server | Mesen2 MCP 0.5.2 |
| Re-run server | Mesen2 MCP 0.6.0, Mesen 2.1.1 |
| Re-run date | 2026-11-01 |

The 0.6.0 run passed. The record is below; the 0.5.2 evidence is kept so the
test remains reproducible against older servers.

## Procedure

1. Start Mesen2 MCP with the ROM and the pack's Lua library:
   `--mcp-lib-dir=<repo>/library/packs/gb/final-fantasy-legend/lua/lib`.
   Add `--mcp-video` only if you need screenshots; the memory probes work
   headless.
2. Load the ROM and confirm `get_rom_info` reports SHA-1
   `901dfc83c72e172d35a376835807fc788444a9bb` and size 131072.
3. Press START at the title and mash A until the world map is visible. The 0.6.0
   run reached it at frame 1709; the counter starts near zero on a fresh load.
4. Save a state with `save_state_file`; keep the sidecar. This is the clean
   field baseline.
5. Run the `reach-field` recipe:
   `run_recipe("reach-field", {}, 1, 10000, true)`.
   Expect `field=true`. In the field `partyHp` is empty because `$D000` is the
   tilemap, not unit records. The clean baseline may report encounter `$00`;
   that is a valid uninitialized map entry, not a failure.
6. Walk east through the Base Town bridge, then into the south forest. Log
   `$FFBD` and confirm the area changes when the map changes. The south forest
   was `$11` in this run.
7. Trigger an encounter. Run `read-record`:
   `run_recipe("read-record", {}, 1, 10000, true)`.
   Expect `inBattle=true`, four party records starting with `$40`, and a slot-4
   enemy record.
8. For a LIZARD encounter, check `enemy.crtype == 0x42`, `enemy.hp` in 38..40,
   and `enemy.maxHp == enemy.hp`. For a ZOMBIE, check `0x78` and 57..60.
9. Compare the party HP values with the on-screen status; they must match.

Recipe headers are not kit-module headers. A recipe loads its kit with
`-- includes: ffl_kit`; `-- requires:` is only for a kit module's own
dependencies. Using `-- requires:` in a recipe leaves the kit unloaded and the
script fails on a nil global.

## Recorded 0.5.2 evidence

- Clean boot to world map at about frame 1901; state saved as
  `ffl-clean-world.mss`.
- Walked LIZARD record: `8B 04 00 27 00 27 00 05 07 04 02 ... 42` at `$D080`,
  HP 39, max 39, stats 5/7/4/2, crtype `$42`.
- Walked ZOMBIE record: `93 08 00 39 00 39 00 09 04 03 06 ... 78`, HP 57,
  at the floor of `[60 - 3, 60]`.
- Party records matched the on-screen 51/51, 20/20, 20/20, 34/34 byte for byte.
- Encounter ids `$11` (GOBLIN) and `$12` (ZOMBIE) were confirmed live;
  ALBATROS can only come from `$15` or `$17`.

## 0.6.0 result

Built from the fork with `dotnet publish McpHost/McpHost.csproj -c Release` and
the native core from `MSBuild Mesen.sln -p:Configuration=Release
-p:Platform=x64 -t:InteropDLL`. The host assembly reports `0.6.0.0`; the
initialize response reports `mesen2-csharp-mcp 0.6.0`, Mesen `2.1.1`.

| Check | Result |
|---|---|
| ROM identity | 131,072 bytes, SHA-1 `901dfc83c72e172d35a376835807fc788444a9bb` |
| Fresh 0.6.0 boot | START at title, A mash, world map at frame 1709, `field=true`, encounter `$00` |
| Saved 0.6.0 baseline | `ffl-clean-world-0.6.0.mss`, sidecar ROM match, reloads at frame 1710 with `field=true` |
| 0.5.2 baseline on 0.6.0 | `ffl-clean-world.mss`, sidecar ROM match, frame 1901 |
| `reach-field` at baseline | `field=true`, encounter `$00`, `partyHp=[]` |
| `reach-field` in south forest | `field=true`, encounter `$11`, `partyHp=[]` |
| Battle found | frame 549,836, encounter `$12`, `inBattle=true` |
| Enemy | sprite `$93`, class 8, crtype `$78` (ZOMBIE), HP 58/58, stats 9/4/3/6 |
| Party | 17/84, 6/69, 13/112, 27/82 |
| On-screen check | screenshot showed exactly 17/84, 6/69, 13/112, 27/82 and `ZOMBIE 1` |

The ZOMBIE HP 58 is inside the expected 57..60 range. Party HP matched the
status window byte for byte. The record layout, crtype values, and encounter id
reading were unchanged from 0.5.2.

### Corrections found by the re-run

- The recipes declared `-- requires:` instead of `-- includes:`. 0.6.0 loads
  recipe kits from the `includes` header field, so the first run returned
  `attempt to index a nil value (global 'ffl')`. Both packs were corrected to
  `-- includes:`.
- `reach-field` originally read the four `$D000` records in the field and
  reported tilemap bytes as HP (`7710` for four identical bytes). It now reports
  party HP only when the battle gate is true.
- The procedure previously required non-zero party HP at the clean field
  baseline and an encounter id in `$10`-`$17`. Both expectations were wrong for
  the field: unit records do not exist there, and the baseline can report `$00`.
  The recipe and this procedure were corrected, not the game data.

### Frame-count note

The 0.5.2 state's sidecar records frame 1901; the fresh 0.6.0 boot reached the
same screen at frame 1709. The difference is the frame counter's origin plus the
asynchronous frames the 0.5.2 server ran between tool calls, not a game or
server behavior change. Both paths show the same starting pocket and report
`field=true`, encounter `$00`, and no field unit records.

A fresh 0.6.0 boot, a state save, and a state reload all passed. Reproducibility
is 20/20.

## Failure signatures

- `field=false` at the clean baseline: the state is a battle or the boot route
  stopped early.
- Four party records do not start with `$40`: the gate is looking at field
  tilemap data.
- A battle looks frozen after A: the cursor is on the invisible `ABIL` row.
  Press B, then DOWN + A.
- The state does not advance and PC is at `$00C9`: the state is crashed, not
  paused.
- HP is above the ladder value: the record is from a different ROM or a patch.
- `attempt to index a nil value (global 'ffl')`: the recipe header says
  `-- requires:` instead of `-- includes:`.
