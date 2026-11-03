# Counselor Library

A game-context library for [Mesen2 MCP](https://github.com/Azarem/mesen2-mcp). It gives an agent enough grounded context to play, test, reverse-engineer, patch, or localize a specific game without wasting thousands of frames on missing information.

This is not a hint line. There are no spoiler gates and no "ask before revealing" rules. A pack is a context dossier: what the game is, how its systems work, where things are, what the numbers mean, how to probe them, and what differs by region. Read what the task needs.

## What is here

| Part | Purpose |
|---|---|
| `packs/` | Per-game context skills, each with `SKILL.md`, references, data, schematics, harnesses or Lua recipes, and source manifests |
| `academy/` | The `counselor-pack-author` master skill, seven lessons, a rubric, and templates |
| `corpus/` | The local, gitignored source library and its ingest/query tools |
| `schemas/` | JSON Schemas for packs, public/local source manifests, and data provenance |
| `tools/` | Scaffold, ingest, query, validate, catalog, bundle, and install scripts |

## Use a pack

From the repository root:

```bash
python library/tools/install_pack.py --pack gb/final-fantasy-legend --target .agents/skills
```

The installer copies the public pack into `.agents/skills/ffl-gameplay/` and prints the `--mcp-lib-dir` value for the pack's Lua kit. Add that path to the Mesen2 MCP server arguments, then start a new session so the client reloads the skill. A harness pack such as SaGa Frontier Remastered prints its harness page instead; it has no Lua kit.

If you already have Azarem's `mesen2-mcp`, copy this `library/` directory into that repository. The library is additive; it does not change the emulator or the MCP server.

## Packs in this release

| Pack | Platform | Status | What it covers |
|---|---|---|---|
| Final Fantasy Legend | GB | certified (97/100) | Route and maps, battle records, monster HP, encounter areas, harness, Lua recipes |
| Secret of the Stars | SNES | certified (91/100) | Systems, world topology, starter data, verified core RAM probes, regional differences |
| SaGa Frontier Remastered | PC / Unity | verified | Save container and field map, ID namespaces, INIT/shops/races, save-file lab, BepInEx plan |

`verified` means the claims are tagged and a field test exists. `certified` additionally requires a rubric score in `CERTIFICATION.md`. See each pack's README for its exact coverage and gaps.

PC/Unity packs use a `target` build identity and a `harness` instead of a ROM block and a Lua kit. The schema change is additive; the GB and SNES packs are unchanged.

## Bring your own corpus

The public repository does not contain copyrighted guides, manuals, maps, ROMs, or saves. It also does not link to them or tell you where to download them.

If you already own reference material, put it in the local corpus:

```bash
python library/tools/scaffold_corpus.py --platform snes --game secret-of-the-stars
python library/tools/ingest_corpus.py --corpus library/corpus --game secret-of-the-stars
python library/tools/query_corpus.py "town data" --game secret-of-the-stars
```

The scaffold creates the category directories. The ingest step builds a local SQLite FTS index. Neither step uses the network, and the index is gitignored.

`library/corpus/README.md` explains the categories and the policy.

## Release bundles

The repository is the full distribution. Tagged releases also provide smaller bundles:

- `counselor-library-vX.Y.Z.zip` - the library without the emulator.
- `counselor-pack-<game>-vX.Y.Z.zip` - one installable pack.
- `counselor-authoring-vX.Y.Z.zip` - the academy, tools, template, and all three example packs (FFL, Secret of the Stars, and SaGa Frontier Remastered).
- `counselor-corpus-vX.Y.Z.zip` - the corpus scaffold and index tools.

Bundles are built from git-known files only, so they cannot contain the local corpus or local manifests. The test suite and its fixtures stay in the repository and are not shipped. See `INSTALL.md` to install one, and `RELEASING.md` for how a library tag publishes the bundles, how that differs from an MCP version bump, and where each artifact appears.

## Licenses

Pack prose, data compilations, schematics, and variants are CC BY-SA 4.0. Tools and Lua code are GPL-3.0. Source metadata remains the source's license; no third-party text is shipped. See `LICENSING.md` and `NOTICE.md`.

## Contributing

See the repository's `CONTRIBUTING.md`. The short version: submit original work or work you have permission to license; never submit ROMs, guides, manuals, maps, saves, or ripped art.
