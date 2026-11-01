---
title: World and route
summary: Base Town exit, east-bank geometry, route order, and map reading.
coverage: partial
---

# World and route

## Route order at the start

1. Start in Base Town.
2. Leave by the **east-wall bridge**: a green plank band across the teal river.
   From the river corner, hold DOWN about four tiles, then RIGHT across the
   planks.
3. The east bank is a forest strip. It is one screen tall: SCY stays at `0` while
   SCX sweeps `0`-`248`. Pushing south hits the map edge; follow the strip east or
   west.
4. The coastline east of the strip is a dead end. Do not follow it expecting a
   crossing.
5. The Town of Hero is south-east of the bridge exit, across the forest band.
   Castle of Shield is just beyond it; Castle of Sword is south-west.

The guide's "south, a little east, keep south" is really **exit east, cross,
then bear south-east**. The east-bank forest and the coastline are the two places
where a blind walker loses time.

## What is verified

| Place | Status | Evidence |
|---|---|---|
| Base Town | walked | party records, `$FFBD` transitions |
| East-wall bridge | walked | SCX/SCY and area change |
| East-bank forest | walked | pinned SCY, sweeping SCX |
| Coastline east | walked | dead end |
| Town of Hero | not reached | overworld sheet geometry only |
| Castle of Shield / Sword | not reached | overworld sheet geometry only |

## Map reading

The local source project has a full sheet set: one folder per area, about 30 PNGs,
compiled by Terran in November 2012. They are stitched screen composites, not
collision maps.

The folder also contains sheets for the sequels. This pack is about the first
game, so use the `FinalFantasyLegend-<World>-<Area>` names.

What the sheets answer:

- world topology: which screen connects to which, where bridges, towns, and
  castles are
- interior layout: doors, stairs, NPCs, chests
- shop stock, prices, and chest contents for each town

What they do not answer:

- whether a tile is walkable
- where a door trigger is
- which screen you are standing on

Pair a sheet with `$FFBD` (the encounter id) to anchor it to the live game.
SCX/SCY then give the position inside one small map.

## Map crops

The local `map-crop.py` helper takes a path, file name, or any unique substring.
It prints the candidates when the hint is ambiguous. Output goes to a local
results folder; no crops are committed.

## Remaining work

- Walk the bridge-to-Town-of-Hero route and record the `$FFBD` transitions.
- Confirm the Castle of Shield and Castle of Sword approaches.
- Add the route to `tests/field-test.md` once walked.
