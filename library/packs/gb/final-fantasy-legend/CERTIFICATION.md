# Certification record

Status: **certified**

Score: 97/100. Rights failures: 0.

| Field | Value |
|---|---|
| Certified | 2026-11-01 |
| Server | Mesen2 MCP 0.6.0, Mesen 2.1.1 |
| ROM | Final Fantasy Legend, The (USA), 131,072 bytes |
| ROM SHA-1 | `901dfc83c72e172d35a376835807fc788444a9bb` |
| Field test | `tests/field-test.md` |
| Rubric | `library/academy/rubric.md` |
| Score | 97/100 |
| Rights failures | 0 |

## Score

| Category | Score | Notes |
|---|---|---|
| Coverage and usefulness | 27/30 | World is partial; Town of Hero not walked |
| Evidence and accuracy | 25/25 | Every table has provenance; 0.6.0 records reproduced |
| Reproducibility | 20/20 | Fresh 0.6.0 boot, state save, and reload all verified |
| Rights and provenance | 15/15 | No local-only files; public credits complete |
| Orientation and clarity | 10/10 | 60-second orientation and read-by-task table |
| **Total** | **97/100** | |

## 0.6.0 evidence

- ROM identity matched: 131,072 bytes, SHA-1
  `901dfc83c72e172d35a376835807fc788444a9bb`.
- A fresh 0.6.0 boot reached the world map at frame 1709. `reach-field`
  returned `field=true`, encounter `$00`, and no party HP (the field tilemap is
  not a unit record). The state was saved as `ffl-clean-world-0.6.0.mss` and
  reloaded at frame 1710 with the same field result.
- The 0.5.2 `ffl-clean-world.mss` also loaded with a matching sidecar at frame
  1901, so the older baseline remains compatible.
- The south-forest state loaded at encounter `$11`.
- A walker found a battle at frame 549,836 in encounter `$12`.
- `read-record` returned four party records and a ZOMBIE: sprite `$93`,
  class 8, crtype `$78`, HP 58/58, stats 9/4/3/6.
- Party HP was 17/84, 6/69, 13/112, 27/82. A screenshot of the battle status
  window showed exactly those values and `ZOMBIE 1`.

## Deduction

- **Coverage 27/30.** The route beyond the east bank and south forest is not
  walked. Town of Hero remains unverified. No other category lost points.

## Conditions

Re-open the certification if the battle record layout, the ZOMBIE crtype, the
encounter table, or the clean-field gate changes. A new ROM hash always requires
a new field test.
