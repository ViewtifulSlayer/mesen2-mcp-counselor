# Lesson 1 - Identify the edition

## Goal

Record a ROM identity that another agent can reproduce.

## Do this

1. Get the file name, size, and SHA-1.
2. Read the internal header: title, mapper, region, ROM size, checksum.
3. Decide whether the image is vanilla, patched, translated, or a beta.
4. Write the identity into `pack.json`.

Example from the FFL pack:

```json
"rom": {
  "title": "Final Fantasy Legend, The (USA)",
  "size": 131072,
  "sha1": "901dfc83c72e172d35a376835807fc788444a9bb",
  "mapper": "MBC2"
}
```

## Rules

- A patched ROM is a different target. Do not field-test a pack against it unless
  the pack is explicitly about the patch.
- A beta or translation is a different target. Record it and declare it.
- If you cannot hash the ROM, mark the identity `[U]` and say why.
- Do not put the ROM in the repository. The hash is the identifier.

## Check

- The SHA-1 is 40 lowercase hex characters.
- The size matches the header's ROM size.
- The mapper is a real value, not a guess.
- `pack.json` and `tests/field-test.md` name the same image.

## Common failure

A state from a 256 KiB patched build is loaded against a 128 KiB vanilla image.
The state may appear to load and then behave like a crash. The hash and size catch
this before the test does.
