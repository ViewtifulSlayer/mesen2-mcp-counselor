# Upstream Baseline

| Field | Value |
|---|---|
| Upstream repository | https://github.com/Azarem/mesen2-mcp |
| Baseline commit | `0c7d9d76ef5680521538378853d2516447e30a8f` |
| Baseline date | 2026-10-30 |
| `mcp-version.txt` | 0.6.0 |
| Fork branch | `master` |

The fork keeps the upstream tree at the repository root. Only `README.md` and
`.gitignore` are edited. The Counselor Library is additive under `library/`.

## Remotes

```bash
# current clone: origin is Azarem
git remote rename origin upstream
git remote add origin https://github.com/ViewtifulSlayer/mesen2-mcp-counselor.git
git fetch origin
git branch --set-upstream-to=origin/master master
```

If you forked through the GitHub UI instead:

```bash
git remote add upstream https://github.com/Azarem/mesen2-mcp.git
git remote set-url origin https://github.com/ViewtifulSlayer/mesen2-mcp-counselor.git
```

## Sync

```bash
git fetch upstream
git merge upstream/master
```

Only the README banner and `.gitignore` additions should conflict. Resolve those
by keeping both the upstream text and the Counselor additions.

Before merging, run a dry check:

```bash
git merge-tree "$(git merge-base HEAD upstream/master)" HEAD upstream/master
```

## Release policy

- Do not bump `mcp-version.txt` for library changes. The library has its own
  `library/VERSION` and `library-v*` tags.
- Do not publish fork binaries in v1. The upstream `Build MCP server` workflow is
  disabled in the fork's Actions settings so pack commits do not build five
  platforms or create duplicate releases.
- The `Release library bundles` workflow builds only library bundles; it does not
  build the emulator.
- If the fork ever changes host code, re-enable the build workflow with path
  filters, bump `mcp-version.txt`, and document the divergence here.

## Tested compatibility

The Final Fantasy Legend pack was originally measured against Mesen2 MCP 0.5.2.
This fork carries 0.6.0. The pack's `pack.json` records both versions and its
`tests/field-test.md` describes the 0.6.0 re-run. Treat the 0.6.0 field result as
pending until the test is recorded on the built server.
