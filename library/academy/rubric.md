# Rubric

100 points. Certification requires at least 80 overall, no category below 60%,
and zero rights failures.

## Coverage and usefulness - 30 points

- All seven domains have an honest coverage value.
- The 60-second orientation is enough to start.
- The read-by-task table points to the right page.
- Gaps are declared, not hidden.
- The pack answers a real question for its target task.

## Evidence and accuracy - 25 points

- Claims carry `[V]`, `[D]`, `[S:id]`, or `[U]`.
- Tables have provenance and match their hashes.
- Guide claims are not presented as ROM facts.
- Corrections are recorded in the changelog.
- A sample claim can be reproduced.

## Reproducibility - 20 points

- The ROM identity is exact.
- The field test names the server version and expected values.
- Lua recipes load from `lua/lib` and declare their kit.
- The route or probe steps are specific enough to repeat.
- No test depends on a state that cannot be identified.

## Rights and provenance - 15 points

- Public manifests have no URL/path/hash for local-only sources.
- No guide text, manual scans, map renders, ROMs, or saves are in the pack.
- CC BY-NC-SA and all-rights-reserved text is absent.
- Schematics are original.
- The local manifest is gitignored.

## Orientation and clarity - 10 points

- The frontmatter description is trigger-rich.
- Terms are defined before they are used.
- Tables are readable without a second document.
- The pack says what not to put in it.
- It does not overwhelm; it routes by task.

## Scoring record

Use `CERTIFICATION.md`:

```md
| Category | Score | Notes |
|---|---|---|
| Coverage and usefulness | 27/30 | ... |
| Evidence and accuracy | 24/25 | ... |
| Reproducibility | 18/20 | ... |
| Rights and provenance | 15/15 | ... |
| Orientation and clarity | 10/10 | ... |
| **Total** | **94/100** | |

Rights failures: 0
```

If the total is below 80 or any category is below 60%, the status stays `draft`
or `verified`.
