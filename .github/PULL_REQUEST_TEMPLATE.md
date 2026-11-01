## What changed

<!-- One pack or one tool change. Name the pack and the pages. -->

## Verification

- [ ] `python library/tools/validate_pack.py --all --template` passes
- [ ] `python library/tools/build_catalog.py --check` passes
- [ ] `python -m unittest discover -s library/tools/tests -v` passes
- [ ] `python library/tools/build_bundles.py --check` passes

## Pack checklist

- [ ] `pack.json` coverage matches what is actually verified
- [ ] Every reference page has `title`, `summary`, and `coverage` frontmatter
- [ ] Every `[S:id]` citation resolves in `sources/manifest.public.json`
- [ ] Declared data files have provenance entries with the current SHA-256
- [ ] The field test records the server version and exact values, or the pack is not marked `verified`
- [ ] `CERTIFICATION.md` has `Score: NN/100` and `Rights failures: 0` if the pack is `certified`

## Rights

- [ ] No ROM, patched ROM, save, savestate, manual, map render, guide text, wiki text, or ripped art is included
- [ ] Local-only sources are credited in the public manifest without a URL, path, or hash
- [ ] Local-only hashes and paths are only in the gitignored `sources/manifest.local.json`
- [ ] Any `permissioned` source has a record under `library/permissions/`

## Not verified

<!-- What remains partial, outline, or [U]? What should the reviewer not assume? -->
