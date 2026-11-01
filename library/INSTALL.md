# Installing the Counselor Library

## From the repository

The library is additive. If you already have Azarem's `mesen2-mcp` checkout, copy the `library/` directory to its root. If you have this fork, it is already there.

Nothing in `library/` changes the emulator, the MCP server, or `mcp-version.txt`.

## Install one pack as an agent skill

```bash
python library/tools/install_pack.py --pack gb/final-fantasy-legend --target .agents/skills
```

The pack becomes `.agents/skills/ffl-gameplay/`. The installer prints the pack's Lua library path. Add it to the Mesen2 MCP server arguments:

```json
{
  "mcpServers": {
    "mesen2-mcp": {
      "command": "dotnet",
      "args": [
        "C:/path/to/MesenMcpHost.dll",
        "--mcp-input",
        "--mcp-lib-dir=C:/path/to/repo/library/packs/gb/final-fantasy-legend/lua/lib"
      ]
    }
  }
}
```

Restart the client after installing so the skill list reloads.

## Release bundles

| Bundle | Contains | Install |
|---|---|---|
| `counselor-library-vX.Y.Z.zip` | `library/` without corpus contents or local manifests | Extract at the root of a `mesen2-mcp` checkout |
| `counselor-pack-<game>-vX.Y.Z.zip` | One pack, `SKILL.md` at the archive root | Extract into `.agents/skills/<skill-name>/` |
| `counselor-authoring-vX.Y.Z.zip` | Academy, schemas, tools, template, and the FFL and Secret of the Stars examples | Extract anywhere; run tools from the extracted `library/` |
| `counselor-corpus-vX.Y.Z.zip` | Corpus scaffold, ingest, query, and schemas | Extract anywhere; point `--corpus` at your local sources |

Every archive has `BUNDLE_INFO.txt` with its version, source commit, contents, and license. Every release has `SHA256SUMS.txt`.

How a release is cut, tagged, and published, and how the library track differs from an MCP server version bump, is in `RELEASING.md`.

## Verify a release

```bash
sha256sum -c SHA256SUMS.txt
```

On Windows PowerShell:

```powershell
Get-FileHash .\counselor-library-*.zip -Algorithm SHA256
```

Compare the value with the matching line in `SHA256SUMS.txt`.

## Local corpus

```bash
python library/tools/scaffold_corpus.py --platform snes --game secret-of-the-stars
python library/tools/ingest_corpus.py --corpus library/corpus --game secret-of-the-stars
python library/tools/query_corpus.py "town data" --game secret-of-the-stars
```

If your sources already live in a folder, use `--adopt`:

```bash
python library/tools/scaffold_corpus.py --adopt path/to/existing/game/folder \
  --platform snes --game secret-of-the-stars
```

That writes a local `corpus.json` pointer to the existing folder. Add `--move` only if you want the categories moved into the canonical scaffold.

The corpus and the index are gitignored. Do not commit them.
