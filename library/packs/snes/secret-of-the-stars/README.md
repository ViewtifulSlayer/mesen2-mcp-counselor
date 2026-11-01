# Secret of the Stars pack

A context pack for *Secret of the Stars* (SNES, USA) and its Japanese release,
*Aqutallion*.

## What it is for

- Understanding the Aqutallion/Kustera party split and the colony layer.
- Playing or testing the early route without losing time to a missing gate.
- Looking up starter character, enemy, item, spell, shop, map, and encounter
  data.
- Writing a RAM probe against the verified addresses without confusing the
  two parties.
- Comparing the JP and US releases.

## Status

**Certified** at 91/100 on Mesen2 MCP 0.6.0 (2026-11-01). The field test booted
a new game to Ray's House and loaded a level-25 Brasca save, then fought and
finished one random battle. The core map, battle, party, battle-pool, and
hero-record addresses matched the screens, and `$02AC` is decoded as the
page-local player coordinate. The remaining local-note addresses are listed as
unverified in `references/harness.md`.

The pack is certified, but the route beyond Ray's House and Brasca is still an
outline, and the Ancient Well has no walked entrance. The score and deductions
are in `CERTIFICATION.md`.

## Coverage

| Domain | Coverage | Notes |
|---|---|---|
| Overview | partial | identity, controls, party model |
| World | partial | route outline and map ids; only Ray's House and Brasca walked |
| Systems | partial | party, colony, battle, menus; no frame-level verification |
| Data | partial | starter tables, 16/16/20/12/12/20/8 rows |
| Harness | verified | core addresses, party slots, battle pools, hero stride |
| Edge cases | partial | verified probe traps, LoROM and region traps |
| Variants | partial | JP/US identity and name pairs; no ROM diff |

## Install

```bash
python library/tools/install_pack.py --pack snes/secret-of-the-stars --target .agents/skills
```

Then add the printed `--mcp-lib-dir` to the Mesen2 MCP server arguments and
restart the client.

## Sources

The full 35-CSV technical set, the six GameFAQs guides, the RPGClassics shrine,
the JP Aqutallion guide, the manuals, and the map renders are local-only. The
public manifest credits them by title and author. Do not commit them.

The JP guide is Shift_JIS. The ingest tool detects it; the public pack includes
only original synthesis and facts.

## License

Pack content is CC BY-SA 4.0. Lua code is GPL-3.0.
