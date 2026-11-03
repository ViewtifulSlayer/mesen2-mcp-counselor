---
title: "English assets"
summary: "The English BaccaratTblData copy, the asset-sourced name tables, and the PC/Steam build used by this pack."
coverage: partial
---

# English assets

This page is about the **English asset copy inside the one PC build**, not a
separate regional release. The game ships both English and Japanese data in the
same `resources.assets`.

## What is English-specific

| Item | Value |
|---|---|
| `BaccaratTblData.bin` Path ID | 1234 |
| Asset file | `SaGa Frontier Remastered_Data/resources.assets` |
| Name tables | Item, character, and area tables are the English/asset spellings |
| Save display names | `saveItemInfoData.CharacterName` is fullwidth Latin, e.g. Asellus |
| Language config | `systemSaveData.configData.language` selects the display language |
| Steam build | app 1295270; local install measured 2026-11-03 |

Path ID 1234 is the English table; 574 is the Japanese table. They are two
copies in the same file, so a tool that opens `resources.assets` must select the
right one. `[S:ffvd-baccarat-skills]`

## Name tables

The item, character, and area names used by `constants.json` are read from
fixed-width ASCII tables in `resources.assets`:

| Table | Offset | Width | Records |
|---|---:|---:|---:|
| Item | 7,738,252 | 16 | 256 |
| Area | 7,782,118 | 20 | 69 |
| Character | 7,783,498 | 16 | 64 |

These are the in-game English spellings. They are authoritative for display:
`T260`, not `T260G`; `AGUNI-CP1`, not `Agni CP1`; `GoldIngot`, not `Gold
Ingot`. The save tool's earlier community table was wrong on many indices and
listed a Katar that does not exist. `[V]`

## What is not English-specific

The save container, the JSON field names, the slot count, the item IDs, the
ability IDs, the map IDs, and the area IDs are the same across languages. The
save is not localized; only the display strings are. `[V]`

## What is still open

- No English-vs-Japanese save pair has been compared field by field.
- The Japanese asset copy has not been opened in this project.
- The language field's exact values are not decoded.
- A console release save is out of scope; the PC/Steam save is the target.

## Sources

- `[S:sfr-save-tool]` for the asset extraction and spelling corrections.
- `[S:ffvd-baccarat-skills]` for the two Path IDs.
- `[S:pcgamingwiki-sfr]` for the platform and Steam app.
- Local: `docs/constants.json`; `docs/gamedata/SaGa Frontier Remastered/...`
  `resources.assets`; `docs/save_layout.md` section 4.
