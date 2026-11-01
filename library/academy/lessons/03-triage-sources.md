# Lesson 3 - Triage sources

## Goal

Decide what can be used, what can be shipped, and what must stay local.

## Three questions

1. **Version:** Is this about the same region and release as the target?
2. **Authority:** Is it a primary source (ROM, official manual) or a secondary
   one (guide, wiki, fan shrine)?
3. **Rights:** What is its license, and does it permit redistribution?

## Source tiers

| Tier | Example | Use | Ship? |
|---|---|---|---|
| ROM | the target image | authority | no |
| Technical data | RAM notes, offset tables | hypotheses to verify | facts only |
| Official manual | scans | context | no |
| Guide | walkthrough, FAQ | route and names | no text |
| Wiki | CC BY-SA text | facts and cross-checks | no text |
| Fan shrine | RPGClassics | facts | no (NC) |
| Community notes | your own observations | evidence | yes, original |

## The rights test

- All-rights-reserved: local-only. Use facts, never text.
- CC BY-NC-SA: local-only. NC is incompatible with a redistributable repo.
- CC BY-SA: facts okay; text only if you accept a mixed-license pack. This library
  does not; write it in your own words.
- Unknown: local-only. Treat it as all-rights-reserved.
- Public domain: facts and text are usable, but still credit.

## The reliability test

A guide can be wrong, outdated, or about a different version. A technical CSV can
be right about an offset and wrong about a name. Cross-check a sample against the
ROM before importing a table.

## Check

- Every source has an ID, title, author, license, region, and language.
- No public manifest entry has a URL, path, or hash for a local-only source.
- The reading plan is topic-level, not a copied table of contents.
- The pack can explain why each source is local-only.

## Common failure

A guide's table is pasted into `data/` because it is convenient. That copies the
source's selection and presentation. Derive the facts, choose your own columns,
and cite the source.
