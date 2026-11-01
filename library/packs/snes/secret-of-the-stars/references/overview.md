---
title: Overview and identity
summary: Release identity, controls, the two-party model, and the scope of this pack.
coverage: partial
---

# Overview and identity

## Release identity

| Field | USA | Japan |
|---|---|---|
| Title | Secret of the Stars | Aqutallion |
| Platform | SNES | Super Famicom |
| Size | 1,572,864 bytes | 1,048,576 bytes |
| SHA-1 | `958a0a835e2e39f382cb37a99098a3cdd4812cf7` | `cb95d1bfd57e0a226fc7322a572032a6d4a149bf` |
| Mapper | LoROM | LoROM |
| Region byte | `$01` | `$00` |

The USA image is the target of this pack. The JP image is a different size and
character set; see `variants/`.

## Controls

- Directions move and select.
- A talks, examines, and confirms.
- B opens or closes the field menu and cancels.
- START opens the main menu.

The field menu has magic, items, equipment, status, and save/load pages. Battle
commands are a separate menu.

## The two-party model

The game is built around two groups:

- **Aqutallion:** the hero party. Ray, Tina, Cody, Leona, Dan, and later recruits.
  The verified slots are `$04A4` through `$04A8`.
- **Kustera:** the colony party. Its slots are `$04A9` through `$04AD`; the
  recruit-flag byte is `$04AE` and the party size is `$04BD`.

The field menu controls one party at a time. A probe that reads only the first
five slots will miss Kustera entirely; a probe that mixes the two ranges will
produce a plausible but wrong party.

## Battle and colony

- Battles use Attack, Defend, Item, Spells, and Unity. Unity is a combination
  magic system with a selected leader and participants (`$0A9F` and `$0AA0`).
- Kustera is a town-building layer. It is not just a second party: recruitment,
  buildings, and the colony roster are part of progression.
- Gold and EP pools in battle are verified at `$0D1F` and `$0D21`. They are
  battle pools, not the save's total gold.

## What this pack covers

- The release identity and the USA/JP split.
- The route outline and the map ids.
- The party, colony, battle, menu, shop, and status model.
- Starter tables for characters, enemies, items, spells, shops, maps, and
  encounters.
- The verified 0.6.0 RAM addresses, hero-record layout, and a Lua probe kit.
- The JP/US name differences that are visible in the local guides.

## What it does not cover

- The full 35-CSV technical set and the full 256-entry encounter table.
- A complete walkthrough. The route outline is a map, not a transcript. Only
  Ray's House and Brasca were walked in the 0.6.0 field test.
- The remaining unverified RAM addresses listed in `harness.md`.
- Sprite, map, or manual data. Those are local-only.

## Related pages

- [World and route](world.md)
- [Systems](systems.md)
- [Data](data.md)
- [Harness](harness.md)
- [Edge cases](edge-cases.md)
