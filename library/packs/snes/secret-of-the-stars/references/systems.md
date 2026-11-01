---
title: Systems
summary: Party structure, colony layer, battle and menu flow, shops, and status.
coverage: partial
---

# Systems

Tags follow `SKILL.md`: `[V]` field-tested, `[D]` documented, `[U]` unverified.

## Party structure

The character table in `data/characters.csv` lists 16 characters with their
class, starting level, EXP, and initial HP. `[D]`

| Character | Class | Notes |
|---|---|---|
| Ray | None | protagonist; starts at level 1 |
| Tina | Banalet | starts at level 1 |
| Cody | None | starts at level 4 |
| Leona | Banalet | starts at level 4 |
| Dan | Wiseman | starts at level 10 |
| David | Warrior | recruit |
| Ryu | Ninja | recruit |
| Ben | Priest | recruit |
| Andy | Fighter | recruit |
| Arthur | Witch | recruit |
| Evelyn | Thief | recruit |
| Jubei | Samurai | recruit |
| Murray | Wizard | recruit |
| Shark | Warrior | recruit |
| Kathy | Archer | recruit |
| Beth | Doctor | recruit |

Classes are not cosmetic: they gate equipment and spell access. `[D]` The byte
at `$5007` is a rank tier, not the job label in `characters.csv`. `[V]` The
0.6.0 field test observed `00` (none) for Ray at level 1, `01` (Pennon) for Ray,
Tina, Cody, and Leona at Brasca, and `04` for Dan. `[V]` The local notes add
`02` Banalet and `03` Aqutalion `[D]`; those two values were not tested, and
`04` is not named there `[U]`.

All 16 hero records live at `$5000` with a verified stride of `$36` bytes. `[V]`
Record `n` is at `$5000 + n * $36`, in character-id order. The field menu shows
only the five party positions `[D]`, but the table holds every character. `[V]`

## Equipment and spells

The offset boundaries below are `[V]`; the item and spell ID meanings and the
trailing bytes are `[U]`.

| Offset | Meaning |
|---|---|
| `$5022` | weapon |
| `$5023` | armor |
| `$5024` | helm |
| `$5025` | shoes |
| `$5026`-`$502C` | seven spell slots |
| `$502D`-`$5035` | nine undecoded trailing bytes |

The weapon/armor IDs in the starter tables are the game's internal IDs, not shop
prices. `[D]` The full equipment tables stay local.

## Battle flow

The battle actions are Attack, Defend, Item, Spells, Unity, and the enemy
phase. `[D]` The local notes place the active action at `$0A57` and `$0A58`;
the 0.6.0 field test did not exercise them. `[U]`

Unity magic uses a leader (`$0A9F`) and a participant bitfield (`$0AA0`) per
the local notes. They were not field-tested. `[U]` It is not an ordinary spell:
the leader and participants must both be set. A probe that reads only the spell
slots will miss it. `[D]`

Escape is resolved from the RNG and a 4-bit comparison, per the local formula
sheet. Repel compares the lead party member's level with the encounter pack's
level. `[D]` These are formulas, not menu labels; verify them before relying on
a specific chance. `[U]`

## Battle rewards

`$0D1F` and `$0D21` are the gold and EP pools used during a battle. `[V]` They
read `0` on the field before a fight even with a rich save; in the 0.6.0 battle
they rose by `84` gold and `80` EP per enemy, held `252`/`240` on the victory
screen, and still read those values after the return to the field. `[V]` They
are not the save's total money. A fresh field load read `0` again. `[V]`

## Field menu

The field menu exposes magic, items, equipment, status, and save/load. `[D]`
The local notes list these menu-related addresses; only the input mirror was
observed in the 0.6.0 run `[V]`:

- `$04B0` cancel button bits `[V]`
- `$04B2` confirm button bits `[V]`
- `$04B4` battle animation toggle (not field-tested) `[U]`
- `$04B5` battle message speed (not field-tested) `[U]`

The button bitfields are an input mirror. The 0.6.0 run read `8000` at `$04B0`
and `0080` at `$04B2` after pressing B and A, and the values latched after
release. `[V]` They are not a menu cursor; do not treat them as a "which command
is selected" answer. `[D]`

## Shops

`data/shops-starter.csv` carries 12 shop rows. `[D]` The local `Shops.csv` has
64 rows and the stock names use the game's short internal spellings, for
example `ShortSwrd`, `LethSuit`, `NomalHat`. `[D]` Preserve those spellings when
matching against the ROM; do not normalize them to guide names.

## Status

The hero condition byte at `$501F` is a bitfield. The labels below are `[D]`;
the bit meanings were not field-verified `[U]`.

| Bit | Status |
|---|---|
| 0 | Poison |
| 1 | Mute |
| 2 | Ill |
| 3 | Daze |
| 4 | Sleep |
| 5 | Stop |
| 6 | Golden |
| 7 | Dead |

Every 0.6.0 test state read `00` `[V]`; the exact interaction rules are not in
this pack `[U]`. Use the bits for detection, not for a cure-order claim.

## Colony

Kustera is a separate progression layer: `[D]`

- party slots `$04A9`-`$04AD` `[V]`
- recruit-flag byte `$04AE`, which read `00` before recruitment and `E0` with
  the five-member Brasca party `[V]`; the notes identify `2X` David and `4X`
  Ryu `[D]`, but those bits are not the whole mask `[U]`
- party size `$04BD`, verified `00` and `05` `[V]`

The colony has its own shops, buildings, and roster. `[D]` A field probe that
only checks the Aqutallion slots will report an empty party when the colony is
active. `[D]`
