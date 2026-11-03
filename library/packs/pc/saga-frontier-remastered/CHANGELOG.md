# Changelog

## 0.1.0 - 2026-11-03

- Added the first PC/Unity Counselor pack, for *SaGa Frontier Remastered*
  (Steam, Unity 2019.4.16f1, IL2CPP metadata 24).
- Added the overview, world, systems, data, harness, and edge-case references,
  plus English/Japanese asset and PS1/Remastered variant pages.
- Added six derived tables: the save field map, sentinels, ID namespaces,
  build identity, known gaps, and the table inventory.
- Added `harness/save_lab.py`: raw DEFLATE inflate/deflate, nested JSON diff,
  and Asellus/T260G fixture assertions.
- Ran the fixture field test: both assertions pass (20/20 and 33/33) and the
  diff helper reaches the inner slot fields.
- Extended `pack.schema.json` additively with `platform: "pc"`, `target`
  (build identity), `harness` (save-file/runtime-bridge scripts), optional
  `lua`, and `tested.harness`. Existing packs validate unchanged.
- Added `.bin` to the forbidden-extension guard so a save cannot be committed
  as pack content.
- Updated `install_pack.py` to install a harness pack without a Lua kit, and
  `check_tree.py` to check declared harness scripts.
- No game binaries, saves, patched assets, guide text, or map renders are in
  the pack.
