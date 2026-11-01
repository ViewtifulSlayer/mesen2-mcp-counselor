# Lesson 5 - Verify in Mesen

## Goal

Turn a claim into evidence.

## The evidence tags

- `[V]` verified live in Mesen or against the ROM image.
- `[D]` derived from a ROM table or formula.
- `[S:id]` sourced from a recorded source.
- `[U]` unverified; must be resolved or declared.

A claim with no tag is a draft, not a pack.

## A verification loop

1. State the smallest claim you can test.
2. Find a probe: a memory value, a screen value, a breakpoint, or a record.
3. Predict the value before you look.
4. Observe it.
5. If it matches, record the address, frames, and ROM hash. If it does not, do
   not adjust the claim to fit; find the wrong assumption.

## The FFL `+1` case

The first three monsters made `+1 = 1 << (hpIndex + 1)` look right. ALBATROS had
HP index 0 and `+1 = 0`, which disproved the rule. The loader and the packed
table at `$71F0` explained it: a class nibble, not a mask.

The lesson is not "check three samples." It is "look for the case that would
disprove you, then test that one."

## Probe hygiene

- Read IO through `emu.read` in Lua; `read_memory` can return `FF`.
- A read breakpoint on IO may never fire. Use an exec breakpoint on the routine.
- A callback sees a PC after the instruction. Subtract the instruction length
  when you need the reading address.
- A state can look paused while the CPU is running away. Check instructions per
  frame and a checksum.

## Check

- Every table row has a provenance entry and a hash.
- Every route claim says whether it was walked.
- The field test names the server version and the exact values.
- A correction has a changelog entry.

## Common failure

A plausible value is treated as verified because it is in a guide. The guide is
`[S:id]`; the ROM is `[V]`. Do not collapse the two.
