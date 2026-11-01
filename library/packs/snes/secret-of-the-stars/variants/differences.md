---
title: Regional differences
summary: Verified JP/US identity and item-name pairs, plus the open comparisons.
coverage: partial
---

# Regional differences

| Area / system | JP | US | Evidence | Confidence |
|---|---|---|---|---|
| Title | Aqutallion | Secret of the Stars | release identity | high |
| ROM size | 1,048,576 | 1,572,864 | local ROM hashes | high |
| Region byte | `$00` | `$01` | ROM headers | high |
| Character set | Japanese | English | ROM text | high |
| Knife | ナイフ | Knife | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Dagger | ダガー | Dagger | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Short sword | ショートソード | ShortSwrd | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Cloth suit | ぬののふく | ClthSuit | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Leather suit | かわのふく | LethSuit | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Hard leather suit | かたいかわのふく | HardSuit | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Hat | ぼうし | NomalHat | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Bread | パン | Bread | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Antidote | どくけし | Antidote | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Rabbit tail | うさぎのしっぽ | RatTail | `[S:jp-guide]`, `[S:landmine-doc]` | high |
| Character names | not compared | Ray, Tina, Cody, Leona, Dan | `[S:landmine-doc]` US only | open |
| Stats | not compared | starter table | `[S:landmine-doc]` US only | open |
| Encounter packs | not compared | 8 starter rows | `[S:landmine-doc]` US only | open |
| RAM addresses | not compared | verified on US; JP untested | `[S:landmine-doc]`, 0.6.0 field test | US verified, JP open |
| Route gates | not compared | guide outline | `[S:guide-darth-ragnarok]` | open |

## How to extend this table

1. Load the JP and US ROMs in two Mesen slots.
2. Compare the same shop inventory and item IDs.
3. Check the first hero block in both; record the class/level/HP pattern. The
   US table starts at `$5000` with a `$36` stride.
4. Walk the first map in both and compare `$040E` and `$043C`. The US values
   are `$0026` at Ray's House and `$00B8` at Brasca.
5. Mark a row `[V]` only after both images agree with the claim. Otherwise keep
   `[U]` and describe the uncertainty.

## What not to assume

- A US address table is not a JP address table.
- A US guide's route is not a JP route.
- The JP guide's Japanese item names are facts, but its prose is local-only; do
  not copy it into the pack.
