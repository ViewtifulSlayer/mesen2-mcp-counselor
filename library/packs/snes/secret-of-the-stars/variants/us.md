---
title: USA release
summary: The verified target image and its English source set.
coverage: verified
---

# USA release

This pack targets the USA release:

| Field | Value |
|---|---|
| Title | Tecmo Secret of the Stars (USA) |
| Size | 1,572,864 bytes |
| SHA-1 | `958a0a835e2e39f382cb37a99098a3cdd4812cf7` |
| Mapper | LoROM |
| Header title | `SECRET OF THE STARS` |
| Region byte | `$01` |

The local USA source set is:

- six GameFAQs files: three full guides, one boss guide, and two patch-code files
- an RPGClassics shrine covering characters, enemies, equipment, items, leveling,
  maps, shopping, treasure, and a ten-part walkthrough
- a RetroMaggedon walkthrough
- a Landmine36 technical document with 35 CSVs and HTML pages
- 58 manual page scans and 2 PDFs
- 137 rendered map images

None of those files are included. The public pack credits them by title and
author; the facts and the starter tables are derived.

## What is verified in this build

- The ROM identity (size, SHA-1, header title, LoROM).
- The core RAM addresses on Mesen2 MCP 0.6.0, including the map id, battle
  flag, game state, party slots, battle pools, and the `$36` hero table.
- The starter tables are faithful transcriptions of the local CSVs, with the
  caveat that the CSV is a secondary source.
- The item-name pairs in `differences.md` are visible in both the JP guide and the
  USA shop data.

## What is not verified

- The JP release's RAM layout.
- The route beyond Ray's House and Brasca. It is an outline from the guides, not
  a fully walked path.
- The full encounter, chest, door, and map tables. Only starters are included.
- The addresses listed as unverified in `references/harness.md`.
