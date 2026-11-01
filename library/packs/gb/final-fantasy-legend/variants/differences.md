---
title: Regional differences
summary: Verified JP/US differences, plus the comparison work that is still open.
coverage: outline
---

# Regional differences

| Area / system | JP | US | Evidence | Confidence |
|---|---|---|---|---|
| Title | Makai Toushi SaGa | Final Fantasy Legend | release identity | high |
| ROM image | separate JP image | 128 KiB USA image | local ROM hashes | high |
| Character names | Japanese | localized | guide text | high |
| Monster names | Japanese | localized | guide text | high |
| Stat tables | not compared | verified subset | `[V]` US ROM | open |
| Encounter ids | not compared | 8 world-1 entries | `[V]` US ROM | open |
| Route order | not compared | partial | `[V]` walk | open |

The local translation-differences FAQ (`[S:faq-gouki-translation]`) is the
starting point for name and text differences. It is not a substitute for a ROM
comparison.

## How to extend this table

1. Load the JP ROM in a second Mesen slot.
2. Compare `crtype` at the US offset and the JP candidate. If the record shape
   matches, check the HP index against `hpvalues`.
3. Walk the same early route and compare `$FFBD` transitions.
4. Record the evidence as `[V]` only after the JP ROM confirms it. Otherwise use
   `[U]` and describe the uncertainty.
