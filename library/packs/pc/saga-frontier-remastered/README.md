# SaGa Frontier Remastered pack

A context pack for *SaGa Frontier Remastered* on PC/Steam (Unity 2019.4.16f1,
IL2CPP metadata v24), scoped to the save tool and data mapping.

## What it is for

- Parsing `SaveData.bin` without confusing the container, the payload, and the
  inner slot blob.
- Mapping `pty`, `ply`, `eventwk`, and `mapwk` fields with their status and
  evidence.
- Resolving item, character, ability, map, area, shop, and monster IDs to their
  namespaces and provenance.
- Checking the flags, INIT sets, shops, Mec/Mystic/Monster records, and
  completion/Fuse state.
- Running a save-file lab that inflates, diffs, and asserts the fixtures
  without launching the game.

This is not a walkthrough and not a mod. The pack does not include the game,
saves, or community guide text.

## Status

**Verified** against the Asellus and T260G fixture contracts on 2026-11-03. The
save lab passes. The live BepInEx/IL2CPP bridge is specified but not built; that
is why `harness` coverage is `partial`. No live-game field test has been run,
and no certification score is claimed.

## Coverage

| Domain | Coverage | Notes |
|---|---|---|
| Overview | verified | Build identity, save-tool scope, three data layers |
| World | partial | Location model and table gaps; no route |
| Systems | partial | State fields mapped; some semantics open |
| Data | verified | ID namespaces, table counts, provenance |
| Harness | partial | Save lab verified; runtime bridge planned |
| Edge cases | verified | Documented traps and do-not-guess list |
| Variants | partial | English/Japanese assets and PS1/Remastered; no console save test |

## Install

```bash
python library/tools/install_pack.py --pack pc/saga-frontier-remastered --target .agents/skills
```

No Lua kit and no `--mcp-lib-dir`. The harness is `harness/save_lab.py`.

## Harness

```bash
python library/packs/pc/saga-frontier-remastered/harness/save_lab.py \
  assert-fixture --fixture asellus \
  --input ../saga-frontier-save-tool/docs/pre-research/SaveData.bin.json
python library/packs/pc/saga-frontier-remastered/harness/save_lab.py \
  diff --left ../saga-frontier-save-tool/docs/pre-research/SaveData.bin.json \
  --right ../saga-frontier-save-tool/docs/pre-research/SaveData.t260g.bin.json
```

The lab uses `zlib` with `wbits=-15` for raw DEFLATE. `deflate` is for building
test files; it is not byte-identical to the game's writer and must not be
treated as a proof of a valid save.

## Sources

The save tool, its 11 runtime tables, the local gameinfo corpus, the fixtures,
and the installed game files are the primary local sources. Public sources are
credited in `sources/manifest.public.json`; local paths and hashes stay in the
gitignored `sources/manifest.local.json`.

## Limits

- The integrity fields (`sfSys.chk*`, `sum`, `pty.sum`) are not understood.
- INIT 3 (BR 4-6) has not been observed.
- The last-clear rank field is not identified.
- Current-area vs scenario-start area is not distinguished by the fixtures.
- 343 `snroFlg` bytes are unnamed.
- The runtime bridge is a plan, not an implementation.

## License

Pack prose and data compilations are CC BY-SA 4.0. The harness and table-build
code is GPL-3.0.
