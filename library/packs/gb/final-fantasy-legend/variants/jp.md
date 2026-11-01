---
title: Japanese release
summary: Known identity of Makai Toushi SaGa and the limits of this pack's JP comparison.
coverage: outline
---

# Japanese release

The Japanese original is **Makai Toushi SaGa** (Makai Toshi SaGa), released for
the Game Boy in 1989. The USA release renamed the game and localized character,
monster, and item names.

This pack has not compared the JP and US mechanics. The local source project has
a translation-differences FAQ (`[S:faq-gouki-translation]`) and a JP guide set;
neither was used to verify stat or route changes for this release.

What is safe to say:

- The JP and US releases are different ROM images.
- Names and text differ; the US guide's names are not a reliable key for a JP
  dump.
- The RAM layout may differ. Do not apply a US address table to a JP ROM without
  verification.

What is open:

- Whether the `crtype` table offsets are identical.
- Whether encounter ids and the `$FFBD` map ids match.
- Whether any stats, item values, or routes changed in localization.
