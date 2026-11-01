# Certification record

Status: **certified**

Score: 91/100. Rights failures: 0.

| Field | Value |
|---|---|
| Certified | 2026-11-01 |
| Server | Mesen2 MCP 0.6.0 |
| ROM | Tecmo Secret of the Stars (USA), 1,572,864 bytes |
| ROM SHA-1 | `958a0a835e2e39f382cb37a99098a3cdd4812cf7` |
| Field test | `tests/field-test.md` |
| Rubric | `library/academy/rubric.md` |
| Score | 91/100 |
| Rights failures | 0 |

## Score

| Category | Score | Notes |
|---|---|---|
| Coverage and usefulness | 24/30 | Six domains are partial; only Ray's House and Brasca were walked, and the well is sealed off |
| Evidence and accuracy | 25/25 | Systems and harness claims carry `[V]`, `[D]`, or `[U]`; tables retain provenance hashes |
| Reproducibility | 18/20 | Fresh boot is exact; the battle path depends on a local level-25 Brasca save |
| Rights and provenance | 15/15 | No local-only files; public manifest has no local paths, URLs, or hashes |
| Orientation and clarity | 9/10 | Strong routing; Pennon, Banalet, and Aqutalion are used as class labels before they are explained |
| **Total** | **91/100** | |

## Evidence

- ROM identity matched: 1,572,864 bytes and SHA-1
  `958a0a835e2e39f382cb37a99098a3cdd4812cf7`.
- A fresh 0.6.0 boot reached Ray's House at frame 6265 with map `$0026`,
  `battleFlag=01`, `gameState=00`, and hero 0 name `A`, rank `00`, HP `32/32`.
- The level-25 Brasca save read map `$00B8`, Aqutallion slots
  `[00,02,01,03,FF]`, Kustera slots `[05,06,07,08,09]`, and Kustera size `05`.
- The first random battle moved `$0020` from `01` to `05` and `$0053` through
  `02`, `03`, and `04`. Victory pools read `252` gold and `240` EP, and the
  party returned to the field.
- `$02AC`-`$02AF` is the player coordinate: big-endian X and Y, 16 units per
  tile, page-local, writable. A step down from `(1040,320)` read `(1040,336)`;
  a blocked step left the pair unchanged.
- The hero table starts at `$5000` with a `$36` stride and 16 records, from
  SABIN through BETH. The kit decodes names, the rank byte, and seven spell
  bytes, and both saved states re-ran through `probe-map` and `read-state`.
- `$043C` is the last encounter, not a battle gate. `$0D1F` and `$0D21` are
  battle pools, not the wallet. `$040E` is 16-bit.
- The systems and harness pages now tag every substantive claim with `[V]`,
  `[D]`, or `[U]`, including per-row evidence for the hero record. The address
  table and table captions carry the same tags.

## Resolved

- **Evidence.** The earlier 89/100 pass deducted three points because systems
  and harness claims used prose labels instead of inline tags. The tagged pages
  close that gap; the evidence category rose from 22/25 to 25/25 without
  changing any factual claim.

## Deduction

- **Coverage 24/30.** The route beyond Brasca is an outline. The Ancient Well
  ring is drawn on the north-east map but a 154-position flood walk found no
  entrance, and the local door table has no Brasca row into `$00BC` or `$0146`.
  The Kustera party was observed in a save, not recruited step by step. The
  late-game route and most map ids were not walked. One point was removed from
  the earlier pass because `$00C0`, previously counted as a walked stage, is a
  stub corridor ending in the void.
- **Reproducibility 18/20.** The fresh boot is repeatable from the documented
  frame and input sequence. The battle run depends on the local
  `sots-brasca-0.6.0.mss` artifact, which is identified but not distributed.
- **Orientation 9/10.** The class names Pennon, Banalet, and Aqutalion are
  introduced in the rank table without a glossary entry.

## Conditions

Re-open the certification if the ROM hash, the `$36` hero stride, the
`$0020`/`$0053` battle gate, the `$040E` map width, the `$02AC` coordinate
layout, or the `$0D1F`/`$0D21` pool meaning changes. A JP field test would raise coverage and regional confidence,
but it is not a condition of this score. A new ROM hash always requires a new
field test.
