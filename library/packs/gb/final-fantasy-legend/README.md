# Final Fantasy Legend pack

A context pack for the USA Game Boy release of *Final Fantasy Legend* (128 KiB
vanilla ROM, SHA-1 `901dfc83c72e172d35a376835807fc788444a9bb`).

## What it is for

- Walking the world map without losing hours to a one-screen strip or a dead-end
  coastline.
- Naming a 32-byte battle record and predicting a monster's HP.
- Surviving the battle command menu, especially the invisible `ABIL` row.
- Harvesting encounters with a batched Lua script.
- Understanding the memory probes and their failure modes before patching or
  tracing the ROM.

## What is verified

| Domain | Coverage | Notes |
|---|---|---|
| Overview | verified | ROM identity, controls, clean-boot route |
| World | partial | Base Town exit and east bank verified; Town of Hero not walked |
| Systems | verified | battle menu, records, HP formula, encounter table |
| Data | verified | HP ladder, five confirmed monsters, eight world-1 encounter entries |
| Harness | verified | measured on Mesen2 MCP 0.5.2, re-checked on 0.6.0 |
| Edge cases | verified | menu trap, `$D000` false positives, IO reads, state crashes |
| Variants | outline | JP release identity only; mechanics not compared |

The 0.6.0 re-run passed and is recorded in `tests/field-test.md`. The pack is
`certified` at 97/100; see `CERTIFICATION.md` for the score. The only remaining
deduction is world coverage beyond the south forest.

## Install

```bash
python library/tools/install_pack.py --pack gb/final-fantasy-legend --target .agents/skills
```

Then add the printed `--mcp-lib-dir` to the Mesen2 MCP server arguments and
restart the client.

## Sources

`guides/` and the Terran map sheets are local-only. The public manifest credits
them by title and author. Place your own copies in the local corpus if you want
the reading plan to resolve:

```bash
python library/tools/scaffold_corpus.py --platform gb --game final-fantasy-legend
```

Do not commit them. The pack's synthesized prose and the verified tables are
self-contained.

## License

Pack content is CC BY-SA 4.0. Lua code is GPL-3.0.
