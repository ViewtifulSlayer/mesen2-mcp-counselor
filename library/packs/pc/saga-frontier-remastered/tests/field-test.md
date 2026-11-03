# Field test

## Target

| Field | Value |
|---|---|
| Game | SaGa Frontier Remastered, PC/Steam |
| Steam app | 1295270 |
| Unity | 2019.4.16f1 |
| Scripting backend | IL2CPP, metadata v24 |
| Build identity | Six hashes in `data/unity-build.csv` |
| Harness | `harness/save_lab.py` 0.1.0 |
| Python | 3.14 (stdlib only) |
| Fixtures | Asellus, T260G (local, gitignored) |
| Date | 2026-11-03 |

This is the first field test for the pack. It verifies the **save-file
contract** and the lab. It does **not** verify a live Unity bridge, which is
why `harness` coverage stays `partial`. No certification score is claimed.

## Procedure

Run from the Counselor repository root (`projects/current/mesen2-mcp`).

1. Assert the Asellus contract:

   ```bash
   python library/packs/pc/saga-frontier-remastered/harness/save_lab.py \
     assert-fixture --fixture asellus \
     --input ../saga-frontier-save-tool/docs/pre-research/SaveData.bin.json
   ```

2. Assert the T260G contract:

   ```bash
   python library/packs/pc/saga-frontier-remastered/harness/save_lab.py \
     assert-fixture --fixture t260g \
     --input ../saga-frontier-save-tool/docs/pre-research/SaveData.t260g.bin.json
   ```

3. Inflate a real container and record the sizes and payload hash:

   ```bash
   python library/packs/pc/saga-frontier-remastered/harness/save_lab.py \
     inflate --input ../saga-frontier-save-tool/docs/pre-research/SaveData.7Characters.bin \
     --output library/tools/tests/tmp/SaveData.7Characters.json --force
   ```

4. Smoke-test the diff on two different fixtures:

   ```bash
   python library/packs/pc/saga-frontier-remastered/harness/save_lab.py \
     diff --left ../saga-frontier-save-tool/docs/pre-research/SaveData.bin.json \
     --right ../saga-frontier-save-tool/docs/pre-research/SaveData.t260g.bin.json \
     --limit 5
   ```

5. Re-hash the six build files and compare with `data/unity-build.csv`.

## Recorded result

### Asellus contract

`20/20 checks passed`. Key values:

| Check | Value |
|---|---|
| `saveDataList.length` | 59 |
| Slot 0 leader / area | 5 / 26 |
| Slot 0 play time | 0h 11m |
| Slot 0 `IsTakeover` | false |
| `pty.money` | 100 |
| `pty.psnCnt` / `heroNo` | 1 / 5 |
| `pty.item_a[0]` | `{itemNo: 7, itemCnt: 1}` |
| `mapwk.imfName` | `imf303` |
| `mapwk.map_name` | 26 |
| `eventwk.mapNo` | 425 |
| `scenarioChartStateArray[157,158]` | set |
| `pty.each.parLev` | 0 |
| Quick room / previous map | `imf1a9` / 132 |
| Auto room / previous map | `imf303` / 425 |

### T260G contract

`33/33 checks passed`. Key values:

| Check | Value |
|---|---|
| Populated snapshots | 5 |
| Leader / area | 6 / 3 on all five |
| Rooms | `imf00c`, `imf00d`, `imf055`, `imf0dd` |
| `pty.each.parLev` | 23 on all five |
| `pty.psnCnt` | 2 or 4 |
| Slot 1 room | `imf055` (Scrap, Junk Shop) |

### Real container inflate

| Field | Value |
|---|---|
| Input | `SaveData.7Characters.bin` |
| Disk bytes | 49,373 |
| Kind | `raw-deflate` |
| Payload bytes | 720,090 |
| Payload SHA-256 | `662f8b6ed712577e4b362f10277a84f6b44affef8ec264a8314c13577bc4997d` |

This confirms the packed container path on a real file, not only on a JSON
mirror.

### Diff smoke

The two fixtures are different saves, so the diff is expected to be large:

| Bucket | Count |
|---|---:|
| Added | 22,156 |
| Removed | 2 |
| Changed | 849 |

The counts are not a regression baseline. They demonstrate that the flattener
reaches the inner slot fields, including `eventwk` and `pty` paths. A real
regression run should diff two snapshots of the same save and ignore the
known-volatile clock paths.

### Build identity

The six files in `data/unity-build.csv` were hashed from the local install and
match the manifest values. `GameAssembly.dll` is 37,480,960 bytes and
`resources.assets` is 144,872,176 bytes.

## Not run

- **Live BepInEx bridge.** No plugin was built, no `dump.cs` was generated, no
  save serialization hook was installed.
- **Live game observation.** No map, flag, or shop value was watched in a
  running process.
- **Japanese asset copy.** Path ID 574 was not opened.
- **INIT 3.** No BR 4-6 clear exists in the fixtures.
- **Last-clear rank.** Not identified.
- **Current-area vs scenario-start.** No fixture crosses areas.
- **Console saves.** Out of scope.

## Failure signatures

- `assert-fixture` says `59 != 61`: the caller counted marker occurrences
  instead of `saveDataList.length`.
- `zlib.error: incorrect header check`: the caller used `zlib.decompress(data)`
  or gzip instead of `wbits=-15`.
- A room name resolves but is wrong: the caller fed `map_name` or `MapNumber`
  to the room table instead of `imfName`.
- A party level reads 0 or a dash: the caller read `pty.parLev`; the live value
  is `pty.each.parLev`.
- A T260G area check fails: the fixture has three numbered slots and two
  quick/auto snapshots; the assertion expects five populated entries.
- A diff is enormous: the two inputs are different saves, not two snapshots of
  one save.

## Artifacts

Local, gitignored, not pack content:

- `docs/pre-research/SaveData.bin.json`
- `docs/pre-research/SaveData.t260g.bin.json`
- `docs/pre-research/SaveData.7Characters.bin`
- `docs/pre-research/SaveData.AsellusFuseComplete.bin.json`
- `docs/pre-research/SaveData.Updated.bin.json`
- `library/tools/tests/tmp/SaveData.7Characters.json` (inflate output)

## Limitations

The lab proves the container, the field paths, and the fixture contract. It
does not prove that an edited save will be accepted by the game, that the
integrity fields are correct, or that a runtime probe can reach the same state.
Those require the staged bridge in `references/harness.md`.
