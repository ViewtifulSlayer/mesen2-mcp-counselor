# Permission records

A source may be included in a pack only when its license allows redistribution
or the rights holder gave written permission. A permission record documents that
permission without reproducing the source.

Public packs do not need a record for local-only sources: those are credited by
title, author, and license, and their content stays out of the repository.

## When to add a record

- The pack includes more than a fact or two from a source that is not already
  under a redistributable license.
- The source is CC BY-NC-SA, all-rights-reserved, or unlicensed.
- The rights holder asked for a specific attribution or scope.

## Record format

Copy `TEMPLATE.md` to `<source-id>.md`. Keep the permission proof itself out of
the repository; record where it is held, not the private correspondence.

The matching public manifest entry uses:

```json
{
  "id": "guide-example",
  "redistribution": "permissioned",
  "permissionId": "guide-example"
}
```

`validate_pack.py` requires `permissionId` for every `permissioned` source.
