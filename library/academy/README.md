# Counselor Academy

The Academy is the authoring half of the library. It teaches an agent or a person
how to turn a game and a pile of sources into a pack that is useful, honest, and
legally clean.

## Start here

- `SKILL.md` is the installable `counselor-pack-author` master skill. It is the
  executable workflow.
- `curriculum.md` is the seven-lesson sequence.
- `rubric.md` is the 100-point review.
- `counselors-code.md` is the short list of principles.
- `templates/game-pack/` is a stub pack that passes validation.
- `checklists/` is the practical review path.

## The workflow in one paragraph

Identify the exact edition and hash the ROM. Inventory the sources you already
have. Triage them for rights and reliability. Read the game before the guides.
Verify the claims in Mesen. Write the six references and the variants. Add data
with provenance, original schematics, and Lua probes. Validate, field-test, and
score. Publish only what you can license.

## What the Academy does not do

- It does not tell anyone where to download copyrighted sources.
- It does not turn a guide into a copy of itself.
- It does not certify a pack without a field test and a rights check.

## Install the master skill

```bash
cp -r library/academy .agents/skills/counselor-pack-author
```

Or point the agent at `library/academy/SKILL.md` directly. The skill is plain
Markdown with frontmatter; it has no code dependencies beyond the library tools.
