# Curriculum

Seven lessons. Each one ends with an artifact that feeds the next.

| Lesson | Question | Artifact |
|---|---|---|
| 1. Identify the edition | Which ROM, region, and version is this? | ROM identity block in `pack.json` |
| 2. Inventory the corpus | What sources do we already have? | `sources/manifest.public.json` draft + local manifest |
| 3. Triage sources | Which are authoritative, and which can we redistribute? | Source tiers and `[U]` list |
| 4. Read the game | What does the player actually see and do? | `overview`, `world`, `systems` notes |
| 5. Verify in Mesen | Which claims survive contact with the ROM? | `[V]` evidence and probes |
| 6. Write the pack | How do we make it usable without overwhelming? | `SKILL.md`, references, data, schematics, Lua |
| 7. Review and certify | Is it accurate, reproducible, and clean? | `CERTIFICATION.md` or a documented gap |

## Lesson 1 - Identify the edition

Hash the ROM, read the header, and record size and mapper. A patched or
translated ROM is not the vanilla target. If you cannot hash the ROM, say so and
mark the identity `[U]`.

## Lesson 2 - Inventory the corpus

Use `scaffold_corpus.py` and `ingest_corpus.py`. Do not browse the corpus by hand
when the index can answer. Record every source you consult, even if you do not
use it.

## Lesson 3 - Triage sources

Three questions:

- Is it about the same region and version?
- Is it a primary source (ROM, official manual) or a secondary one (guide)?
- What is its license, and does it allow redistribution?

A high-quality guide can still be local-only. A technical CSV can be useful and
still not redistributable. Facts can be re-derived; expression cannot be copied.

## Lesson 4 - Read the game

Play or observe enough to answer: what are the controls, what is the first goal,
what does the menu do, and what does one map transition look like? A guide can
tell you the route; only the ROM can tell you the frame.

## Lesson 5 - Verify in Mesen

A claim is `[V]` only when the ROM confirms it. A table value is `[D]` when it
comes from a ROM offset. A guide claim is `[S:id]` even if it is correct. When a
guide and the ROM disagree, measure.

The FFL `+1` correction is the model: the first three records made a mask rule
look right; ALBATROS disproved it; the loader and the packed table settled it.

## Lesson 6 - Write the pack

Write `SKILL.md` first. It must answer: what is this, how do I start, what do I
read for my task, and what are the traps? Then write the six references. Add data,
schematics, and Lua only after the prose is honest.

## Lesson 7 - Review and certify

Run the validator, the page-index check, and the field test. Score the rubric.
Rights failures block certification regardless of the score. Record what is
pending. A `verified` pack with declared gaps is a success; a `certified` pack
with an unrun field test is a lie.
