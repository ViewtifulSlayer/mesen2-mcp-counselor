---
title: Data and tables
summary: The starter tables, their fields, and how to extend them from the local 35-CSV set.
coverage: partial
---

# Data and tables

The full technical set is 35 CSV files in the local corpus. This pack carries a
starter subset so an agent can orient without the corpus. The subset is facts,
not a copy of the source's presentation.

## Starter tables

| File | Rows | Fields |
|---|---|---|
| `data/characters.csv` | 16 | id, name, class, level, initial EXP, later EXP, current HP |
| `data/enemies-starter.csv` | 16 | id, name, HP, MP, attack, defense, speed, species, hit count |
| `data/items-starter.csv` | 20 | id, name, type, targeting, description |
| `data/spells-starter.csv` | 12 | id, name, MP, power |
| `data/shops-starter.csv` | 12 | shop, item count, item list |
| `data/map-ids-starter.csv` | 20 | id, map name |
| `data/encounters-starter.csv` | 8 | id, pointer, unknown bytes, three monsters |

## Reading the tables

- IDs are the game's internal IDs, usually two hex digits. Do not assume a
  decimal ID when a table says `0A`.
- Enemy stats are base values. They are not the final battle values after
  equipment, buffs, or species modifiers.
- `hit count` is the number of hits, not a damage multiplier.
- `current HP` in the character table is the starting current HP, not the max.
- Spell `power` is the raw table value; the damage formula uses the caster's
  stats and the target's resistance.
- Shop names use the game's short spellings (`ShortSwrd`, `NethSuit`, `NomalHat`).
  Preserve them.

## What is not in the starter subset

- The full 128-row enemy table.
- The full 45-row item table and 49-row weapon / 53-row armor tables.
- The full 256-row encounter pack table.
- The 150-row chest table with flag ids.
- The 974-row exit-door table.
- The 337-row map id table.
- The 98-row level/EXP and spell-learning tables.

Those stay local. The `sources/reading-plan.md` points to the right files.

## Extending a table

1. Read the local CSV and identify the columns.
2. Check the ROM table address in the local `Rom Data Map.csv`.
3. Verify a sample row in Mesen before importing the whole table.
4. Add a provenance entry with the source file and a hash of the derived table.
5. Do not copy the CSV wholesale. Re-derive the facts and keep the source's
   presentation out of the repository.

The local technical document is a secondary source. The ROM is the authority.
