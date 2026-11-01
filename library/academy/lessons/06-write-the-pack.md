# Lesson 6 - Write the pack

## Goal

Make a pack that an agent can use under time pressure without reading all of it.

## Write `SKILL.md` first

It needs:

- a trigger-rich description
- the 60-second orientation
- a read-by-task table
- the source-ID legend
- the corpus status
- the pages table
- the quick checks
- what not to put in the pack

If `SKILL.md` is bad, the references do not matter; the agent will not know which
one to open.

## The six references

| Page | Question |
|---|---|
| `overview.md` | What is this, how do I start, what is out of scope? |
| `world.md` | Where do I go, what connects to what? |
| `systems.md` | How do battles, menus, and progression work? |
| `data.md` | What do the numbers mean, and where are the tables? |
| `harness.md` | How do I probe this game in Mesen? |
| `edge-cases.md` | What will waste my time if I do not know it? |

## Task-based depth

- Beginner: `SKILL.md` + `overview`.
- Normal: `world` + `systems`.
- Advanced: `data`.
- Expert: `harness`.
- Ultra-specific: `edge-cases`, `variants`, and the local corpus.

Do not add a spoiler gate. Do not make the agent ask permission to read.

## Data and schematics

Data tables get their own columns and a provenance entry. Schematics are original
SVG; they are not traced renders. If a table or map comes from a local source, the
public pack carries the facts and the credit, not the file.

## Lua

Put the kit in `lua/lib/<game>_kit.lua`; put recipes in `lua/lib/recipes/`. A
recipe starts with `-- requires: <kit>`. Test the recipe in Mesen if you can. If
you cannot, mark it `[U]` and say what would verify it.

## Check

- Every reference has `title`, `summary`, and `coverage` frontmatter.
- Every `[S:id]` resolves in the public manifest.
- The page index is fresh.
- The pack does not contain a guide, manual, map render, ROM, or save.
- The data tables match their provenance hashes.

## Common failure

The pack is a single 5,000-word page. It is accurate and unusable. Split it by
task and put the orientation at the top.
