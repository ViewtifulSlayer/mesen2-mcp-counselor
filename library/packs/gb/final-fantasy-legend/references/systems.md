---
title: Systems
summary: Battle menu, record layout, HP construction, encounter areas, and fleeing.
coverage: verified
---

# Systems

## The battle command menu

`FIGHT` / `ABIL` / `RUN`, stacked vertically. The middle `ABIL` row renders
invisibly. The hand appears to sit on `FIGHT` while the selection is one row
lower. The cursor's row is remembered, so it is not necessarily on `FIGHT` when a
battle opens.

What that means in practice:

- **A on `ABIL`** opens the ability list. For a character with no abilities the
  window is drawn empty, nothing can be confirmed, and the battle appears frozen.
  This is the single most expensive trap in the game.
- **B** backs out one level, including out of the empty window.
- **DOWN + A** selects `RUN` and is the reliable way out of a fight.
- A blind A-mash eventually selects `FIGHT` and wins a low-level battle, but it
  stalls the moment it lands on `ABIL`.

For unattended work, flee instead of fighting. Every record is built at battle
start, whether or not you attack, so a walk-harvest loop only needs to survive the
battle. `DOWN`-then-`A` cycles produce `ran` / `Can't run` and end the fight
within a few rounds.

## Battle records

32-byte slots at `$D000`. Slots 0-3 are the party; slot 4 (`$D080`) is the first
enemy. These records exist only in battle. In the field `$D000` is the tilemap,
so a party HP read there is meaningless.

| Offset | Meaning |
|---|---|
| `+0` | sprite/graphics byte (not the record index) |
| `+1` | class nibble from the `$71F0` table: `0/1/2/4/8` |
| `+3..+4` | current HP |
| `+5..+6` | max HP (equal to current at build time) |
| `+7..+10` | str, def, agi, mana |
| `+31` | the crtype index; the cheapest way to name a dump |

The party slots match the on-screen HP byte for byte. That is a free sanity
check that a dump is a real battle, not scene data.

`+31` is written by the loader and is the identity key. `+0` is the sprite byte
copied from the source record; two records can share stats, so check both when
matching against `crtype`.

## HP construction

```
v = hpvalues[crtype[i][1]]          ; the ladder value
s = (v >= 4096) ? 255 : v >> 4      ; the cap is on the HIGH byte
r = round(rand * s / 256)           ; one RNG step, r in 0..s inclusive
HP = v - r                          ; always in [v - (v >> 4), v]
```

HP never exceeds the ladder value and can sit up to about 6 percent below it. A
"missing" point of HP is variance, not a miscalculation. The `CP $10` test is on
the high byte, so `v >= 4096` saturates at 255 rather than shifting to 256 or
beyond.

## Encounter areas

The current map's encounter id sits in HRAM `$FFBD`. It changes when the map
changes, so logging it every frame turns a walk into a survey of area boundaries.

| Symbol | Address | Meaning |
|---|---|---|
| encounter id | `$FFBD` | current map's entry (0-127) |
| entry | file `$1A868`, 5 bytes each | 3 monster ids + 2 count bytes |

The decoded world-1 entries are in `data/encounters-world1.csv`. All eight share
one low-level pool; the ids differ in which monsters you meet, not in level.

## What `+1` is not

`+1` is a per-monster class nibble from the packed table at `$71F0`, not a copy of
the HP index and not an HP mask. The loader computes:

```
HL = $71F0 + (monsterIndex >> 1)
A  = (monsterIndex odd) ? (byte & $0F) : (byte >> 4)
dest[1] = A
```

The table only holds `0, 1, 2, 4, 8` (`0` x100, `4` x30, `8` x30, `2` x22,
`1` x18). The first three confirmed monsters make `1 << (hpIndex + 1)` look
plausible; ALBATROS disproves it. Do not derive anything from `+1`; index the
table with the crtype id if you need the class.
