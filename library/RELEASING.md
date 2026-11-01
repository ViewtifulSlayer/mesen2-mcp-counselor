# Releasing

This repository ships two things on two independent tracks. They share a
repository but not a version, a tag, or a workflow.

| Track | Version file | Tag | Workflow | Release |
|---|---|---|---|---|
| Mesen2 MCP server | `mcp-version.txt` | `vX.Y.Z` | `.github/workflows/build.yml` | Five platform zips |
| Counselor Library | `library/VERSION` | `library-vX.Y.Z` | `.github/workflows/library.yml` | Five bundle zips |

Nothing is uploaded by hand. Both workflows build on the runner and publish
with `GITHUB_TOKEN`; no secrets are configured and none are needed.

## The library track

### What triggers it

- Any push to `master` that touches `library/**`, the workflow, the root
  `README.md`, or `.gitignore` runs the `validate` job.
- Any pull request that touches `library/**` or the workflow runs `validate`.
- A push of a tag matching `library-v*` runs the `release` job instead.
- `workflow_dispatch` runs `validate` on demand.

### What `validate` checks

1. `library/tools/check_tree.py` - every directory the template and each pack
   declare exists and is tracked, so a clean checkout keeps it.
2. `validate_pack.py --all --template` - pack schema, sources, provenance
   hashes, forbidden files.
3. `build_catalog.py --check` - `CATALOG.md`, `PAGE_INDEX.md`, `catalog.json`,
   and `ATTRIBUTIONS.md` match the packs.
4. `python -m unittest discover -s library/tools/tests` - the tool suite.
5. `build_bundles.py --check` - builds every bundle in a temp directory and
   inspects it for corpus content, local manifests, and forbidden extensions.

### What `release` does

1. Refuses to continue unless the tag equals `library/VERSION`. A
   `library-v0.1.1` tag on a tree whose `library/VERSION` says `0.1.0` fails
   immediately.
2. Runs the validator, the catalog check, and the test suite (the bundle
   inspection is skipped because the build itself follows).
3. Builds the bundles into the runner's `dist/` with the bare version number
   (`--version "${GITHUB_REF_NAME#library-v}"`).
4. Creates the GitHub release `library-vX.Y.Z` with `--generate-notes`, attaching
   every `dist/*.zip` and `dist/SHA256SUMS.txt`.

### Cutting a library release

```bash
# 1. Bump the version and describe the change.
#    library/VERSION, library/CHANGELOG.md, each pack's CHANGELOG.md,
#    and library/release-notes/<version>.md

# 2. Rehearse locally.
python library/tools/check_tree.py
python library/tools/validate_pack.py --all --template
python library/tools/build_catalog.py --check
python -m unittest discover -s library/tools/tests
python library/tools/build_bundles.py --version 0.1.1 --out /tmp/bundles
python library/tools/build_bundles.py --version 0.1.1 --check /tmp/bundles
rm -rf /tmp/bundles

# 3. Commit and push, then wait for the push run to go green.
git add -A library
git commit -m "Release the Counselor Library 0.1.1"
git push origin master

# 4. Tag the exact commit the push run validated.
git tag library-v0.1.1
git push origin library-v0.1.1

# 5. Attach the curated notes (CI publishes generated notes).
gh release edit library-v0.1.1 --notes-file library/release-notes/0.1.1.md
```

The workflow that runs is the one stored in the tagged commit, so commit a
workflow fix before you tag, never after.

### Moving a tag

Allowed only while no release exists for that tag, for example when the release
job failed before `gh release create`. Nothing was published, so moving the tag
changes nothing anyone could have downloaded:

```bash
git tag -f library-v0.1.0 HEAD
git push origin :refs/tags/library-v0.1.0
git push origin library-v0.1.0
```

The middle command deletes the remote tag and the last one recreates it. Anyone
who already fetched the old tag has to delete it locally
(`git tag -d library-v0.1.0`) and fetch again.

Once a release exists, do not move the tag. GitHub keeps the release pointing at
the old commit, download counts and checksums stop matching the tag, and anyone
who already fetched it has a different tree. Bump `library/VERSION` and cut the
next version instead.

## The MCP server track

### What triggers it

Every push to `master`, every pull request, and manual dispatch. There is no
path filter, so every push builds all five platforms: `win-x64`, `linux-x64`,
`linux-arm64`, `osx-x64`, `osx-arm64`.

Each job compiles the native core, publishes the framework-dependent host,
verifies the release contents, runs the MCP smoke test, zips the result, and
uploads it as the artifact `mesen2-mcp-<rid>`.

### What publishes

The `release` job runs after a green matrix and only on a push to `master`. It
reads `mcp-version.txt` and checks for an existing `vX.Y.Z` release:

- Release already exists: nothing is published, the push is just a build.
- No release yet: it downloads all five artifacts, refuses to continue unless
  every `<rid>.zip` is present, writes `SHA256SUMS.txt`, and creates `vX.Y.Z`
  with `--generate-notes`.

The release carries five zips, one per platform, plus `SHA256SUMS.txt`. The zips
are framework-dependent: the host needs the .NET 8 runtime, and Linux and macOS
need SDL2.

### Cutting a server release

```bash
# 1. Bump the version.
#    mcp-version.txt and MCP_TOOLS_CONTRACT.md (and the release notes if you keep them)
# 2. Commit, push, wait for all five builds to pass.
# 3. The release job publishes vX.Y.Z by itself.
```

To correct a bad server release, bump `mcp-version.txt` again. Deleting the
release and re-running the same version is possible but leaves the tag and the
artifact history inconsistent; prefer a new patch version.

The macOS runners are pinned deliberately: `macos-15` for arm64 and
`macos-15-intel` for x64. The macOS 14 images were retired on 2026-11-02 and
jobs requesting them are cancelled.

## Where artifacts appear

| Artifact | Location | Retention |
|---|---|---|
| Server zips (`mesen2-mcp-<rid>.zip`) | The build run's Artifacts section | Repository default, 90 days |
| Server release assets | Releases page, tag `vX.Y.Z` | Permanent |
| Library bundle zips | Releases page, tag `library-vX.Y.Z` | Permanent |
| Bundle checksums (`SHA256SUMS.txt`) | Same release as the zips | Permanent |
| CI logs | The Actions run | Repository default |

A local `dist/` directory is scratch space. The runner builds into its own
`dist/` and discards it after upload, so anything in your working copy is a
rehearsal and must never be uploaded to a release by hand.

### The "Latest" badge

GitHub marks one release per repository as Latest, and `/releases/latest`
resolves to it. Two tracks share this repository, so the library release is
created with `--latest=false`: the server download links in the README must
never resolve to a library-only archive. If an older library release already
holds the badge, edit it on the Releases page and clear "Set as the latest
release", or run `gh release edit <tag> --latest=false`.

## Bundle contents and naming

Library bundles carry the library version; pack bundles carry each pack's own
`packVersion` from its `pack.json`, which is why they do not move with the
library version.

| Archive | Contents |
|---|---|
| `counselor-library-v<lib>.zip` | The whole public library, including both packs |
| `counselor-authoring-v<lib>.zip` | Academy, schemas, tools, template, both packs |
| `counselor-corpus-v<lib>.zip` | Corpus scaffold, schemas, ingest and query tools |
| `counselor-pack-<pack>-v<pack>.zip` | One pack, `SKILL.md` at the archive root |

Every archive carries `BUNDLE_INFO.txt` with its version, the source commit, the
file count, and the license. Bundles are built only from git-known files, use
fixed timestamps, and sort their entries, so the same commit produces
byte-identical archives.

## If a run fails

| Symptom | Cause | Fix |
|---|---|---|
| `tag library-vX.Y.Z does not match library/VERSION` | Version file not bumped | Bump `library/VERSION`, commit, move the tag if nothing published |
| `Tree check failed ... missing directory` | A directory exists only on your disk | Add the content or a `.gitkeep`, commit it |
| `Catalog ... is stale` | Pack pages changed | Run `python library/tools/build_catalog.py` |
| `provenance sha256 does not match` | A data table was edited without updating its hash, or the checkout rewrote line endings | Regenerate the hash in `data/provenance.json`; `.gitattributes` pins the tables to LF, so a stale copy needs a re-checkout |
| `Version mismatch: tag/--version ...` | A caller passed the tag name instead of the version | Pass the bare version, or copy the workflow step, which strips the prefix |
| macOS job cancelled | Retired runner image | Use `macos-15` or `macos-15-intel` |

## Rules

- Never commit or upload `dist/`, `library/corpus/`, or a `manifest.local.json`.
- Never move a tag that already published a release.
- Never tag a commit whose `library/VERSION` does not match the tag.
- Never edit `CATALOG.md`, `PAGE_INDEX.md`, `catalog.json`, or `ATTRIBUTIONS.md`
  by hand; `build_catalog.py` owns them.
- The library tag does not touch the emulator, and a `mcp-version.txt` bump does
  not touch the library. They can ship in the same push without interfering.
- A library release never takes the "Latest" badge; the server release keeps it.
