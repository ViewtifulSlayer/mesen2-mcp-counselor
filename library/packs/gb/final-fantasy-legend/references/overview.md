---
title: Overview and identity
summary: ROM identity, controls, save behavior, clean boot, and the scope of this pack.
coverage: verified
---

# Overview and identity

## ROM

| Field | Value |
|---|---|
| Title | Final Fantasy Legend, The (USA) |
| Platform | Game Boy |
| Size | 131,072 bytes |
| SHA-1 | `901dfc83c72e172d35a376835807fc788444a9bb` |
| Mapper | MBC2 |
| Header ROM size | `$02` (128 KiB) |
| Cart type | `$06` |

The pack targets the vanilla 128 KiB image. The patched 256 KiB build used in
the source project is a different ROM and must not be substituted for field
tests. A state made against one image will not load against the other by
default.

## Controls

- Directions move.
- A talks, examines, and confirms.
- B cancels and opens the field menu.
- START opens the main menu.

## Clean boot

Load the ROM, press START, and mash A through the intro. About 900 frames of
mashing reaches the world map. Save a state there. That state is a reproducible
walking baseline; the older `docs/savestates/` states in the source project are
crashed mid-battle, not menu states.

## What this pack covers

- The Base Town exit, the east bank, and the known world-1 encounter areas.
- The battle command menu and its invisible row.
- The 32-byte battle record and the monster HP derivation.
- The `hpvalues` ladder and eight world-1 encounter entries.
- Mesen MCP probes, batching, and the traps that produce false results.

## What it does not cover

- The Town of Hero was not reached in the 2026-11-01 session. The overworld sheet
  settles the geometry, but the walk is not recorded.
- The full 200-row monster name table is not reproduced here. The guide's
  Appendix C is the local source; the verified subset is in `data/`.
- The Japanese release's mechanics are not compared. See `variants/`.
- Save-state editing and patching are separate skills; this pack gives the
  gameplay and memory context they need.

## Related pages

- [World and route](world.md)
- [Systems](systems.md)
- [Data](data.md)
- [Harness](harness.md)
- [Edge cases](edge-cases.md)
