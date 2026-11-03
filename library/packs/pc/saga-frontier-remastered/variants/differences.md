---
title: "Regional and version differences"
summary: "What changes between PS1 and Remastered, English and Japanese assets, Steam and console, and one build and the next."
coverage: partial
---

# Regional and version differences

## PS1 original vs Remastered

| Aspect | PS1 | Remastered (PC) |
|---|---|---|
| Save medium | Memory card blocks | `SaveData.bin` raw DEFLATE + JSON |
| Field access | Fixed offsets in a binary record | Named JSON paths |
| Map IDs | Same id space | Same id space; 0x303 is Chateau Aiguille in both |
| Character record | 256-byte binary record | JSON object with the same semantic fields |
| Item/ability tables | Binary/table formats | `resources.assets` name tables + community tables |
| Integrity | Memory-card checksum | `chk*`/`sum`, algorithm unknown |

The PS1 documents are **corroboration, not authority**. The Remastered save is
JSON, so there is no fixed record stride; the PS1 256-byte layout describes the
same semantics, not the same bytes. Where the PS1 table and the Remastered asset
table disagree on spelling, the asset table wins. `[V]`

The map ID space is the strongest continuity: 0x303 is the same room in both,
so there is no Remastered offset. The room table still has source gaps (425 is
one), and those are not version shifts. `[V]`

## English vs Japanese assets

| Aspect | English | Japanese |
|---|---|---|
| `BaccaratTblData.bin` Path ID | 1234 | 574 |
| Name tables | English asset spellings | Japanese asset spellings |
| Flag dictionary | English gloss layer (draft) | CP932 source, verbatim |
| Save format | Same | Same |
| Language field | `configData.language` | `configData.language` |

Both copies are in one `resources.assets`. This is an asset selection problem,
not a regional release. `[S:ffvd-baccarat-skills]`

## Steam vs console

This pack targets the PC/Steam build. Console saves are platform-encrypted and
are out of scope. Do not apply a PC field map to a console save without
decrypting it and re-verifying the container. `[U]`

## Build drift

A Steam update can change the executable, `UnityPlayer.dll`, `GameAssembly.dll`,
the IL2CPP metadata, `globalgamemanagers`, or `resources.assets`. The pack pins
SHA-256 for all six in `data/unity-build.csv`. If a hash changes:

1. Re-measure the six hashes.
2. Re-check the name-table offsets and record counts.
3. Re-run the fixture assertions.
4. Re-check the IL2CPP metadata version before using a dump.
5. Treat old offsets and method signatures as suspect.

`[V]`

## What is not known

- No JP save has been compared with an English save.
- No console save has been decrypted or tested.
- The `language` field's exact values are not decoded.
- The build-to-build stability of `resources.assets` offsets is not measured
  beyond the local install.

## Sources

- `[S:sfr-save-tool]` for the PS1/Remastered continuity and the asset table.
- `[S:ffvd-baccarat-skills]` for the English/Japanese Path IDs.
- `[S:pcgamingwiki-sfr]` for the PC platform identity.
- Local: `data/unity-build.csv`; `docs/save_layout.md` sections 4 and 8;
  `docs/constants.json`.
