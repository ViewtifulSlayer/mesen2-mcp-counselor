---
title: "Japanese assets"
summary: "The Japanese BaccaratTblData copy, the CP932 flag source, and the language-specific cautions."
coverage: partial
---

# Japanese assets

This page is about the **Japanese asset copy inside the one PC build**, not a
separate regional release. The game ships both copies in the same
`resources.assets`.

## What is Japanese-specific

| Item | Value |
|---|---|
| `BaccaratTblData.bin` Path ID | 574 |
| Asset file | `SaGa Frontier Remastered_Data/resources.assets` |
| Flag dictionary source | `bf386d29fa5f29d5.txt`, CP932 encoded |
| Flag labels | Japanese block names and meanings, kept verbatim |
| Language config | `systemSaveData.configData.language` |
| Save display names | The save can carry fullwidth Latin or Japanese names |

The flag dictionary is the main Japanese-language artifact in the pack. It is
CP932, not UTF-8. The 169 named bytes, 440 bit entries, and 345 state entries
were parsed from it; the English gloss is a separate draft layer, not a
replacement for the Japanese source. `[V]` `[D]`

## Asset selection

Path ID 574 is the Japanese table; 1234 is English. A tool that edits or reads
`BaccaratTblData.bin` must select the intended copy. Opening the wrong one
changes the table you are looking at, not the save format. `[S:ffvd-baccarat-skills]`

## Text handling caution

The localization restoration mod notes an ASCII/SHIFT_JIS conversion routine
that can hard-freeze on mixed text. This is not a save-tool concern, but it is
a reason not to inject arbitrary text into the game during a mapping probe.
`[S:ffvd-sfr-modding]`

## What is not Japanese-specific

The container, the JSON keys, the slot count, the IDs, and the area/room model
are the same. The save is not localized; the display strings are. `[V]`

## What is still open

- No Japanese save has been compared with an English save.
- The Japanese asset copy has not been opened in this project.
- The `language` field's exact values are not decoded.
- Japanese item and ability names have not been reconciled with the English
  asset names.

## Sources

- `[S:sfr-save-tool]` for the CP932 flag parse and the 169/440/345 counts.
- `[S:ffvd-baccarat-skills]` for the two Path IDs.
- `[S:ffvd-sfr-modding]` for the text-conversion freeze.
- Local: `docs/flag_names.json`; `docs/gameinfo/discord/bf386d29fa5f29d5.txt`;
  `docs/save_layout.md` section 4.10.
