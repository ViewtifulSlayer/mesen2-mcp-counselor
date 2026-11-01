# Lesson 7 - Review and certify

## Goal

Decide whether the pack is ready, and say honestly what is not.

## The review sequence

1. `python library/tools/validate_pack.py --all`
2. `python library/tools/build_catalog.py --check`
3. `python -m unittest discover -s library/tools/tests -v`
4. Run `tests/field-test.md` on the target ROM.
5. Score the rubric.
6. Record the result in `CERTIFICATION.md`.

## Certification

`certified` requires:

- score >= 80/100
- no category below 60%
- zero rights failures
- a passing field test on the named ROM and server version

If any condition is missing, the status stays `verified` or `draft`. That is not
a failure; it is an accurate state.

## What to record

- The server version.
- The ROM SHA-1 and size.
- The exact values that were checked.
- The checks that could not run, and why.
- The next action that would close the gap.

## Rights review

- Public manifest: no URL/path/hash for local-only sources.
- No guide text, manual scans, map renders, ROMs, or saves.
- No CC BY-NC-SA text.
- Original schematics.
- Local manifest is gitignored.

A rights failure blocks certification even if every technical test passes.

## Check

- `CERTIFICATION.md` has a score and `Rights failures: 0`.
- `pack.json` status matches the evidence.
- The catalog shows the right status.
- The field test is not a placeholder.
- The changelog says what changed.

## Common failure

The pack is marked `certified` because the tables look right. No field test was
run. The status is a claim; do not make a claim you cannot reproduce.
