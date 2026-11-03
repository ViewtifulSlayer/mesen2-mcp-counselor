---
title: "Overview"
summary: "Release identity, save-tool scope, the three data layers, terminology, and how to route a task."
coverage: verified
---

# Overview

## What this is

*SaGa Frontier Remastered* is Square Enix's 2021 remaster of the 1997
PlayStation game. The PC release is a Unity build with an IL2CPP scripting
backend. This pack is written for the **save tool and data mapping**, not for a
playthrough and not for asset modding. `[S:sfr-save-tool]`

The save tool is a static, client-side HTML5 viewer. It reads a save, keeps a
pristine backup, parses a working copy, and never writes back. Its public
surface is 19 files and 11 JSON tables. The pack exists so an agent can work on
that tool without loading the 2,200-line runbook, the 594-line save layout, and
the 1,000-line agent state on every task. `[S:sfr-save-tool]`

## Identity

| Field | Value | Evidence |
|---|---|---|
| Title | SaGa Frontier Remastered | `app.info` |
| Platform | PC / Steam, 64-bit | `[S:pcgamingwiki-sfr]` |
| Steam app | 1295270 | `[S:pcgamingwiki-sfr]` |
| Unity | 2019.4.16f1 | `globalgamemanagers` |
| Scripting backend | IL2CPP | `GameAssembly.dll` + `global-metadata.dat` |
| Metadata version | 24 | metadata header |
| Save container | Raw DEFLATE (RFC 1951) | fixture |
| Payload | JSON text | fixture |
| Inner slot | JSON string, second parse | fixture |

The six measured file hashes are in `data/unity-build.csv`. The executable is
`SaGa Frontier Remastered.exe`; the IL2CPP metadata is
`SaGa Frontier Remastered_Data/il2cpp_data/Metadata/global-metadata.dat`. These
hashes pin the build better than a title and a version string. `[V]`

A Steam update can change any of the six. If a hash does not match, treat the
pack's offsets and table counts as suspect until re-measured.

## The three data layers

Do not collapse these into one:

| Layer | Form | What to do |
|---|---|---|
| On disk | Raw DEFLATE stream, no zlib/gzip header | `zlib.decompress(data, -15)` or `DecompressionStream('deflate-raw')` |
| Payload | JSON text with four root keys | `JSON.parse` once |
| Slot | `saveDataJsonStr`, itself a JSON string | `JSON.parse` a second time |

The root keys are `systemSaveData`, `saveDataList`, `quickSaveData`, and
`autoSaveData`. `saveDataList` has 59 entries; quick and auto are separate, so
there are 61 slot-shaped entries in total. `[V]`

Byte-offset reasoning belongs to the compressed container, not to the payload.
There is no fixed record stride in the JSON. `DataView` is useful for the byte
inspector, but not for addressing a character or item field. `[V]`

## What the pack covers

| Domain | Coverage | What it means |
|---|---|---|
| Overview | verified | Build, layers, scope |
| World | partial | Location model; no route |
| Systems | partial | Stored systems; some semantics open |
| Data | verified | ID namespaces and table counts |
| Harness | partial | Save lab verified; runtime bridge planned |
| Edge cases | verified | Traps and failure signatures |
| Variants | partial | English/Japanese assets; no console test |

## Terminology

- **File**: one `SaveData.bin`, containing the system block and all snapshots.
- **Slot**: one entry in `saveDataList`, or the quick/auto entry.
- **Payload**: the inflated JSON text.
- **Inner blob**: the JSON string inside `saveDataJsonStr`.
- **Area**: the coarse zone index in `mapwk.map_name` and `MapNumber`.
- **Room**: the current map asset in `mapwk.imfName`.
- **Roster**: the 41 `ply` records. It is not the active party.
- **Party**: the `psnCnt` entries named by `chrNo`, `companionChrNo`, `team`.

## Route by task

- First contact or build check: this page, then `data/unity-build.csv`.
- Location bug: `world.md`, then `edge-cases.md`.
- Party, flags, shops, INIT, races: `systems.md`.
- ID or name resolution: `data.md`.
- Inflate, diff, assert, or live probe: `harness.md`.
- A value looks plausible but wrong: `edge-cases.md` before changing code.

## Sources

- `[S:sfr-save-tool]` is the primary public source: the save tool, its docs,
  and its 11 runtime tables.
- `[S:pcgamingwiki-sfr]` is used only for the platform and engine identity.
- The local runbook, save layout, agent state, gameinfo tree, fixtures, and
  installed build are recorded in `sources/manifest.local.json`.

## What this page does not cover

The route, the battle system, the story, mod installation, asset editing, or
console save encryption. Those are separate tasks.
