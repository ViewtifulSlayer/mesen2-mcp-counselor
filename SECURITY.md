# Security Policy

## What this repository ships

The fork contains the Mesen2 MCP server at the repository root and the additive
Counselor Library under `library/`. The library ships Python tools, JSON
schemas, Markdown, SVG, CSV, and Lua recipes. It does not ship a ROM, a save, a
guide, or a network service.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting on this repository. Do not open a
public issue for an exploitable problem.

Include:

- The affected path or tool.
- The version or commit.
- A minimal reproduction that does not contain a ROM, save, or copyrighted file.
- The impact you believe it has.

Relevant library issues include path traversal in the corpus tools, unsafe
archive extraction in the installer or bundle builder, validator bypasses that
let a forbidden file into a pack, and index or bundle content leaking a
`manifest.local.json` or corpus file.

For the emulator and MCP server itself, also check whether the issue exists in
[Azarem/mesen2-mcp](https://github.com/Azarem/mesen2-mcp) and report it there if
the fork did not introduce it.

## What not to send

- ROMs, patched ROMs, keys, BIOS files, saves, or savestates.
- Manual scans, guide text, or map renders.
- Credentials, tokens, or personal data.

If a proof of concept needs a game file, describe the file's properties instead
of attaching it.

## Supported versions

The library is validated on the Python version in
`.github/workflows/library.yml` and on the Mesen2 MCP versions listed in each
pack's `pack.json`. Older tags are not patched; fixes land on `master` and in the
next `library-v*` release.
