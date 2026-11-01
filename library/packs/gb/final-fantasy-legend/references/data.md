---
title: Data and tables
summary: The hex bracket calibration, HP ladder, confirmed monsters, and encounter entries.
coverage: verified
---

# Data and tables

## The one calibration that unlocks the guides

The Monster Inventory FAQ lists every monster as `NAME [xx]`, and those brackets
are **hexadecimal crtype indices**, not decimal.

- `LIZARD [42]` is crtype index `66` decimal.
- `ZOMBIE [78]` is crtype index `120` decimal.

Verify a row cheaply: the FAQ's `hp` column is the ladder value from
`hpvalues`, and its four stats are `crtype[+2..+5]`. When both match, the row is
the right monster.

## ROM tables

| Table | File offset | Shape | Notes |
|---|---|---|---|
| `crtype` | `$1AAE8` | 200 x 9 B | `+0` sprite, `+1` hp index, `+2..+5` str/def/agi/mana |
| `hpvalues` | `$1B254` | 32 x u16 LE | the HP ladder |
| `$71F0` class table | `$1B1F0` | 200 nibbles, 2 per byte | `0/1/2/4/8` |
| encounter entries | `$1A868` | 5 B each | 3 monster ids + 2 counts |

## HP ladder

The full 32-value table is in `data/hp-ladder.csv`. The out-of-order tail
matters: index 22 is 250 and index 23 is 600, so the ladder is not monotonic
past 21.

Variance:

| v | s = v >> 4 | HP range |
|---|---|---|
| 20 | 1 | 19-20 |
| 40 | 2 | 38-40 |
| 60 | 3 | 57-60 |
| 82 | 5 | 77-82 |
| 103 | 6 | 97-103 |
| 202 | 12 | 190-202 |
| 501 | 31 | 470-501 |
| 1000 | 62 | 938-1000 |
| 2500 | 156 | 2344-2500 |
| 5000 | 255 (capped) | 4745-5000 |

## Confirmed monsters

`data/monsters-confirmed.csv` carries the verified rows. The confirmed set is
not the full bestiary; it is the set checked live or against the ROM tables.

| crtype | FAQ tag | Name | HP | str/def/agi/mana |
|---|---|---|---|---|
| `$42` (66) | `[42]` | LIZARD | 40 | 5/7/4/2 |
| `$4E` (78) | `[4e]` | GOBLIN | 20 | 9/6/4/3 |
| `$78` (120) | `[78]` | ZOMBIE | 60 | 9/4/3/6 |
| `$9B` (155) | `[9b]` | ASIGARU | 20 | 5/6/8/3 |
| `$BF` (191) | `[bf]` | BYAK-KO | 1000 | 50/45/50/50 |

Observed builds include LIZARD at 40, 39, and 38; GOBLIN at 20 and 19; ZOMBIE at
59, 58, and 57. Both ends of the random range occur in ordinary play.

## Encounter entries

`data/encounters-world1.csv` carries the eight world-1 entries. Which of the
three slots actually spawns was not determined; all eight share one low-level
pool.

## Extending the table

`Appendix C - Full munster listing, file order` in the Monster Inventory FAQ is
ordered by crtype index, so it is already sorted the way the ROM is. For a batch
conversion, parse `NAME [xx]` plus the `hp` field and compare against
`hpvalues` to catch a row where the tag is not what you assumed.

Do not copy the FAQ's table into the repository. Derive the facts, record the
provenance, and cite the source by ID.
