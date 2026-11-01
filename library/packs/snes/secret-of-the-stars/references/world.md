---
title: World and route
summary: Route outline, the walked Brasca segment, verified map ids, and the well that cannot be entered from town.
coverage: partial
---

# World and route

The route below combines a guide outline with a **walked Brasca segment** from
the 0.6.0 field test on 2026-11-01. The walk verified `$00B8` (Brasca) and
`$00BB` (Brasca House 2). The Ancient Well was **located and approached but not
entered**: the ring is drawn on Brasca's north-east map, the tree wall blocks
every approach from town, and the local door table has no Brasca entry into the
well. `$00BC`-`$00BF` and `$0146` remain table ids, not walked gates.

`$00C0` was reached earlier from a world-map cave, but it is a narrow corridor
that ends on a one-tile platform in the void. It is not the Sealed Cave that
connects to the well, and the earlier field test overstated it. Treat the rest
of the outline as orientation, not proof that every gate works.

## Route outline

| Stage | Location | What changes | Source |
|---|---|---|---|
| 1 | Heart Island, Ray's House | name entry, first items, Likado lead | `[S:guide-darth-ragnarok]` |
| 2 | Likado | shops, David, the first party errand | `[S:guide-darth-ragnarok]` |
| 3 | Jeep Volcano | first dungeon, fire shrine lead | `[S:guide-darth-ragnarok]` |
| 4 | Beegees / Old Hill | recruits, hospital, lab, colony setup | `[S:guide-darth-ragnarok]` |
| 5 | Decatas | shops, rocket, east-continent access | `[S:guide-darth-ragnarok]` |
| 6 | Fire / Water / Wind / Earth shrines | elemental gates | `[S:landmine-doc]` map ids |
| 7 | Kustera | colony party and town building | `[S:landmine-doc]` party slots |
| 8 | Booth Castle | late-game gate | `[S:guide-darth-ragnarok]` |

The guide part titles are a useful sequence check: Heart Island, Save the
Children, The Farmer Baz, It's Not A Circus, Leona, The East Continent,
Aqutallion Rises, The Search for Dr. Ash, Booth, Thieves! Women!.

## Walked Brasca segment

Starting point: the level-25 Continue save, file 1, at the Brasca south
entrance (`$00B8`, frame 1896). The save is a verification artifact, not pack
content. The first upward step from that save is blocked by the sign and tree
line; the sequence below is the working way around it.

| Gate | From | Input observed | Result | Evidence |
|---|---|---|---|---|
| South entrance to interior | `$00B8` south entrance | right 70, down 30, right 70, up 60, then up 60 | map stays `$00B8`; party reaches the north edge | `sots-brasca-east.png`, `sots-brasca-north.png` |
| North edge to House 2 | `$00B8` north edge | left 120, up 120 | `$00BB` Brasca House 2 | `sots-brasca-house2.png` |
| Town to world map | `$00B8` south edge | down through the gate | `$0000` overworld | `sots-desert-1.png` |

The south-entrance sequence does not change the map id; it is a navigation
gate, not a map transition. The House 2 row is a real map transition read
through `$040E`.

The Ancient Well ring is drawn at the top of the north-east clearing
(`sots-brasca-north2.png`, `well-b1.png`). The ring sits behind a continuous
hedge, with forest along the east edge. A one-tile flood walk of the town
covered 154 distinct positions and produced no map change; up and right were
blocked at every position tested, and the ring itself was never stood on. The
local door table has no row whose source is `$00B8`: every row into `$00BC`
names source `$80`, the overworld flag. The ring is scenery in town; the Lava
Cave is entered from the overworld. That matches the walk and the guide line
"head northeast from Uncle Save's house until you see a well". The well is
**located and approached, but its entrance is not in the town map**.

The earlier `$00C0` row is withdrawn. That map was reached from a world-map
cave, but walking it leads up a narrow corridor to a one-tile platform in the
void (`c0-north.png`); there is no exit and no connection to `$0146`.
`$00C0` is a reachable map id, not a walked dungeon stage.

## Map ids

The local technical document lists 337 map ids. The starter table in
`data/map-ids-starter.csv` carries the first 20. Examples:

| ID | Map |
|---|---|
| `00` | The Overworld |
| `01` | The Floating World |
| `04` | Heart Island Cave |
| `05` | Likado |
| `0E`-`11` | Jeep Volcano and summit |
| `12` | Aris Shrine |
| `14` | Beegees Secret Tunnel |
| `18` | Dr. Gari's Lab |
| `19` | Old Hill Hospital |
| `1E` | Kuster House |
| `2E`-`31` | Fire, Water, Wind, Earth shrines |
| `32` | Beegees |

The map id is 16-bit at `$040E`. The encounter id is 8-bit at `$043C`.

### Verified map ids

| ID | Map | Evidence |
|---|---|---|
| `26` | Ray's House | Fresh 0.6.0 boot, frame 6265 |
| `B8` | Brasca | Level-25 continue save, frame 1896; south entrance and north edge |
| `BB` | Brasca House 2 | Walked from `$00B8` north edge, 2026-11-01 |
| `C0` | Sealed Cave | Entered from a world-map cave; stub corridor ending in void, not a well gate |

The starter table stops at `$13`; the verified ids were checked against the
full local 337-row table.

### Located, not entered

| ID | Map | Status |
|---|---|---|
| `146` | Ancient Well | Ring drawn on the Brasca north-east map; hedge and forest block every approach walked; no door row from `$00B8` |
| `BC` | Lava Cave | Door table says overworld source (`$80`); the overworld tile was not walked |
| `BD`-`BF` | Switch Rooms 1-3 | Table ids only; no walked entrance |

## What the route does not tell you

- Which NPC opens a gate. The local guides have the dialogue order; this
  outline only names the stages.
- Which chests are missable. The local chest CSV has the flag ids; the starter
  pack does not reproduce them.
- Whether a route works on the JP release. The JP map ids and event flags were
  not compared.
- How to enter the Ancient Well. The town ring is scenery; every door row
  into `$00BC` comes from the overworld (`$80`), so the entrance is a world-map
  feature north-east of Brasca. The exact overworld tile was not walked, and
  `$0146` remains a table id.

## Known gaps

- Brasca (`$00B8`) and Brasca House 2 (`$00BB`) are walked. The Ancient Well
  (`$0146`) is located but not enterable from town, and `$00BC`-`$00C0` have
  no walked entrance that reaches it. The rest of the route is a guide outline.
- The Kustera recruitment sequence is documented; the five-member party was
  observed in a local save, not recruited step by step.
- The late-game route is a guide outline, not a field test.
