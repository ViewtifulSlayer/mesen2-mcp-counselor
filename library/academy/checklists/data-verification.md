# Data verification checklist

- [ ] The table has a schema chosen for this pack, not the source's layout.
- [ ] The source file and ROM offset are recorded.
- [ ] The generator script is named or the manual transcription is described.
- [ ] A sample row was checked against the ROM or a live value.
- [ ] The table's SHA-256 matches `data/provenance.json`.
- [ ] Names and IDs use the game's spelling, not a normalized guess.
- [ ] Variants (region/version) are kept separate or declared.
- [ ] The table is listed in `pack.json` under `data`.
- [ ] No full source CSV was copied.
