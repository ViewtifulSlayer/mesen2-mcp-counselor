---
title: "Harness"
summary: "The save-file lab, raw DEFLATE rules, diff and fixture recipes, and the staged BepInEx/IL2CPP runtime bridge plan."
coverage: partial
---

# Harness

## What works now

`harness/save_lab.py` is a stdlib-only Python tool. It does four things:

| Recipe | What it does |
|---|---|
| `inflate` | Raw DEFLATE to JSON text |
| `deflate` | JSON text to a raw DEFLATE test file |
| `diff` | Flatten two saves and report added, removed, and changed leaves |
| `assert-fixture` | Check the Asellus or T260G contract |

It does not launch the game and does not write a real save. `deflate` is for
building test inputs; it is not byte-identical to the game's writer.

## Container rules

The on-disk file is **raw DEFLATE (RFC 1951)**: no zlib header, no gzip header,
no trailer. The first byte is compressed data, often `0xED`, not `{`.

```python
import zlib
payload = zlib.decompress(open("SaveData.bin", "rb").read(), -15)
```

The `-15` is the whole trick. `zlib.decompress(data)` and `gzip.decompress(data)`
both fail with "incorrect header check". In a browser,
`DecompressionStream("deflate-raw")` is the equivalent and has been verified
lossless in headless Chrome. `[V]`

The inflated payload is JSON. The inner slot is a JSON **string**:

```python
outer = json.loads(payload)
slot = json.loads(outer["saveDataList"][0]["saveDataJsonStr"])
```

There is no fixed record stride in the payload. Byte offsets are diagnostic,
not identifiers; they shift with any edit. Count `saveDataList.length` for the
slot count, not the number of `saveDataJsonStr` marker occurrences. The marker
is 61 because quick and auto are included, while the list is 59. `[V]`

## Commands

Run from the Counselor repository root:

```bash
python library/packs/pc/saga-frontier-remastered/harness/save_lab.py inflate \
  --input SaveData.bin --output SaveData.json

python library/packs/pc/saga-frontier-remastered/harness/save_lab.py diff \
  --left ../saga-frontier-save-tool/docs/pre-research/SaveData.bin.json \
  --right ../saga-frontier-save-tool/docs/pre-research/SaveData.t260g.bin.json

python library/packs/pc/saga-frontier-remastered/harness/save_lab.py assert-fixture \
  --fixture asellus \
  --input ../saga-frontier-save-tool/docs/pre-research/SaveData.bin.json
```

`diff` flattens nested objects and arrays into dotted paths. It parses
`saveDataJsonStr` by default; `--no-parse-inner` keeps the raw slot strings. The
output is sorted and limited by `--limit` (default 200), so a large save does
not flood a terminal.

`assert-fixture` checks the contract in `tests/field-test.md`: slot 0 leader 5,
money 100, party count 1, first item 7, current room `imf303`, area 26, previous
map 425, and the chart indices. The T260G check is deliberately weaker: it
accepts any populated slot whose area is 3 and whose room is one of 12, 13, 85,
or 221, because the fixture has several snapshots.

## What the lab does not do

- It does not validate or recompute `chk*` or `sum`.
- It does not prove that an edited save will be accepted by the game.
- It flattens every slot by default. Use `--no-parse-inner` to keep the raw
  slot strings; for a single slot, extract it before diffing.
- It does not include the fixtures. They are local, gitignored research.

## Runtime bridge plan

There is no polished, game-agnostic runtime MCP for a shipped Unity build. The
credible path for this game is a game-specific BepInEx 6 IL2CPP plugin. The
attachment is proven; the control surface is not.

### Evidence

BepInEx issue #229 was opened on 2021-04-16 against **SaGa Frontier Remastered
v1.0, Steam build 6443908**, with **BepInEx 6.0.0 x64 Bleeding Edge 361**. The
IL2CPP preloader crashed while parsing the game's version strings, which carry
extra data. The fix was merged the next day and the issue was closed. That
proves the preloader can attach; it does not prove a plugin can read the save
model or drive input. `[S:bepinex-issue-229]`

No public BepInEx/MelonLoader plugin, Harmony patch, or IL2CPP dump for this
title was found. The modding scene edits `resources.assets` and
`BaccaratTblData.bin` with UABE/BNE2/PPF, not code. `[S:ffvd-sfr-modding]`

### Stage 0 - save lab

Already implemented. Use it for every field-map change before touching the
game. It is the regression net.

### Stage 1 - read-only bridge

1. Run Il2CppDumper 6.7.x against `GameAssembly.dll` and
   `global-metadata.dat`. Keep `dump.cs` and `DummyDll` local; do not commit
   them. `[S:il2cppdumper]`
2. Build a BepInEx 6 IL2CPP plugin with `BasePlugin` from
   `BepInEx.Unity.IL2CPP`. Reference the generated `BepInEx/interop`
   assemblies after the first launch.
3. Expose a loopback HTTP API with a per-session token:
   - `GET /health` - process, scene, build hash.
   - `GET /state` - scene name, `mapwk.imfName`, player position.
   - `GET /flags` - nonzero `snroFlg` bytes with values.
   - `GET /save/snapshot` - the serialized save as the game sees it.
   - `GET /screenshot` - a PNG captured on the main thread.
4. Hook save serialization/deserialization and `snroFlg` writes with Harmony.
   Log the calling method, the field/offset, and the before/after value.
5. Bind `127.0.0.1` only. Refuse `0.0.0.0`. Do not add a write endpoint yet.

`bepinex-mcp` is a useful reference for the HTTP shape, stable hierarchy
selectors, and dynamic patches. It does not provide screenshots, input, or
frame-step, so it is a reference rather than a dependency. `[S:bepinex-mcp]`

### Stage 2 - controlled writes

Only after Stage 1 is stable:

- Change one field at a time; snapshot before and after.
- Let the game write its own save so the integrity fields are computed by the
  game, not by the tool.
- Work on copies. Keep a pristine `SaveData.bin` and hash it before and after.
- Generate the blocked fixtures: INIT 3 (BR 4-6), a second Fuse route, the
  NG+/additional-content matrix, and a post-area-change save.
- If a checksum method is identifiable in `dump.cs`, call it and compare its
  output with the four `chk*` fields. That is the shortest path to the write
  path.

### Stage 3 - MCP wrapper

Expose the HTTP API as MCP tools with stable selectors and snapshot/diff. Add
input and frame control last, not first. The highest-value tools are state
read, flag diff, save snapshot, and screenshot; walking the player is less
important than setting the state a test needs.

## Launching

- Steam: `steam://rungameid/1295270`, or the executable directly.
- BepInEx injects through its doorstop at process start; no separate launcher.
- Windowed mode is safer for screenshots: `-screen-fullscreen 0`.
- Do not use `-batchmode` or `-nographics` for this retail build; the game
  expects a renderer and a window.

## Safety

- Read-only first. Writing a live save before the integrity algorithm is known
  can corrupt the only copy.
- Keep a backup outside the game's save folder. The game rotates `.bak0`-`.bak2`
  but that is not a substitute.
- Hash the build before and after an update. A changed `GameAssembly.dll` can
  invalidate offsets and method signatures.
- Do not distribute game binaries, generated interop assemblies, or dumps.

## What is not proven

- A BepInEx 6 plugin has not been built or run for this build.
- No `dump.cs` has been generated in this project.
- The save serialization method and the checksum method are not identified.
- Input injection and frame stepping are not implemented.
- The current BepInEx 6 bleeding-edge build may differ from the 2021 build in
  the issue; pin and record the exact version.

## Sources

- `[S:bepinex-issue-229]` for the proven attachment and the exact version.
- `[S:bepinex-mcp]` for the HTTP/MCP reference implementation.
- `[S:il2cppdumper]` for the dump path.
- `[S:ffvd-sfr-modding]` for the asset-edit modding context.
- Local: `docs/save_layout.md` section 10; `docs/project_runbook.md` section 7.
