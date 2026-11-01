# Lesson 4 - Read the game before the guides

## Goal

Write an orientation that matches what the player actually sees.

## Do this

1. Load the ROM and reach the first field screen.
2. Record the controls and the first goal.
3. Open each menu once and note what it contains.
4. Walk one map transition and record the probe that changes.
5. Trigger one battle and record the command menu.
6. Only then read the guide's route.

## Why

A guide describes a route in prose. The ROM describes the screen, the menu state,
and the frame. If you write the pack from the guide alone, you inherit its
assumptions: a different version, a skipped menu, a route that assumes a item you
do not have.

The FFL pack is the model: the guide says "south, a little east"; the ROM shows a
bridge on the east wall, a one-screen forest strip, and a dead-end coastline. The
pack records the geometry, not the prose.

## What to capture

- The exact boot sequence and frame count if you can.
- The first menu and the first battle command.
- One map id or encounter id transition.
- One party HP or status value that matches the screen.
- The failure mode that cost you time.

## Check

- The 60-second orientation can be followed without the guide.
- The first goal is a verb, not a chapter title.
- At least one probe is anchored to a visible value.
- The route does not claim a walk you did not do.

## Common failure

The pack says "go south" because the guide says so. The map is one screen tall
and south is a wall. Walk it, then write it.
