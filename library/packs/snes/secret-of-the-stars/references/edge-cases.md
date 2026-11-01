---
title: Edge cases
summary: Verified-probe traps, party-slot confusion, hero stride, battle pools, LoROM layout, and region differences.
coverage: partial
---

# Edge cases

## Core addresses are verified; do not generalize

The addresses in the verified table in `harness.md` were checked on Mesen2 MCP
0.6.0 against the USA ROM. That does not make every nearby byte safe. A value
can still look right and be wrong: a map id read as one byte can look valid on
an early map, and an empty party slot (`FF`) can be mistaken for a character.

Before a patch or a long script:

1. Load the USA ROM.
2. Read the candidate address and the value on screen.
3. Change one thing in game and read it again.
4. Record the evidence. Only then move it from "Still unverified" to the
   verified table.

## Party slots are positions, not a roster

`$04A4`-`$04A8` are Aqutallion positions 1-5; `$04A9`-`$04AD` are Kustera
positions 1-5. Each value is a character id (`00` Ray, `01` Tina, `02` Cody,
`03` Leona, `04` Dan, `05` David, ...). A probe that reads `$04A4`-`$04AD`
and filters out `FF` will produce a mixed party. Use
`sots.aqutallionSlots()` and `sots.kusteraSlots()` separately.

At Brasca the Aqutallion bytes were `00 02 01 03 FF`, which is Ray, Cody, Tina,
Leona in party order. Do not sort the ids and call that the party.

## Empty is FF, not 00

Ray's House reads `[00, FF, FF, FF, FF]`: character `00` is Ray, and the four
empty positions are `FF`. The same rule applies to Kustera. `00` is a valid
character id (Ray), not "empty".

## Map id is 16-bit

`$040E` is 16-bit little-endian. Reading `$040E` alone gives the low byte. The
high byte is at `$040F`. A map id that stays below `$100` can be a genuine low
map, so "below `$100`" is not proof of a bad read. The failure is a map above
`$FF` read as one byte.

Verified values: `$0026` Ray's House and `$00B8` Brasca.

## Encounter id is sticky

`$043C` read `00` in Ray's House, `79` at the random battle, and still `79`
after the party returned to the field. It is the current or most recent
encounter, not a battle gate. Use `$0020` and `$0053` together for that.

## Battle gold and EP are pools

`$0D1F` and `$0D21` read `0` on the field in Brasca even though the save had
money. They rose by `84` gold and `80` EP per enemy defeated and stayed at
`252`/`240` after victory. Do not use them as the party's total gold or as a
wallet editor. The kit calls them `battleGold` and `battleEp`.

## Hero records use a fixed stride

The 16 hero records start at `$5000` and are `$36` bytes apart. Record `n` is
at `$5000 + n * $36`; BETH, the last, starts at `$532A`. The record holds seven
spell bytes at `+$26`-`+$2C` and nine undecoded trailing bytes at
`+$2D`-`+$35`. Do not infer the stride from the name length or write past the
spell slots.

The name uses `40` + ASCII and terminates with `FF`. The seventh name byte is
unused and can glitch; do not write it.

## The two releases are not interchangeable

| | USA | Japan |
|---|---|---|
| Title | Secret of the Stars | Aqutallion |
| Size | 1,572,864 | 1,048,576 |
| SHA-1 | `958a0a...` | `cb95d1...` |
| Character set | English | Japanese |

Do not apply a US address table to the JP ROM because the header says LoROM. The
ROM size and text encoding differ. The JP guide is Shift_JIS; the ingest tool
detects it, but the pack does not include the text. The JP addresses were not
tested in the 0.6.0 run.

## LoROM offsets are not file offsets

A LoROM CPU address and a file offset are different spaces. The local technical
document mixes both in places. When a table says `0x70110`, check whether it is a
file offset or a CPU address before using it in `emu.read`.

## Shops use internal spellings

`ShortSwrd`, `LethSuit`, `NomalHat` are the game's short strings, not typos.
Normalizing them to `ShortSword`, `LeatherSuit`, `NormalHat` will make a lookup
fail. Preserve the source spelling and map display names separately.

## Status bits are detection, not a cure order

The condition byte at `$501F` has eight bits. The local notes list poison, mute,
ill, daze, sleep, stop, golden, and dead. All 0.6.0 test states read `00`, so
the bit meanings are not field-verified. Use the bits for detection, not for a
cure-order claim.

## Kustera is not a second Aqutallion

The colony has its own slots, flag byte, party size, and town state. `$04AE`
read `00` before recruitment and `E0` with five Kustera members; it is a flag
mask, not a count. A script that assumes one party will work in the field but
fail the moment the colony is active.
