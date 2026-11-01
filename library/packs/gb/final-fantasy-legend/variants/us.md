---
title: USA release
summary: The verified target: 128 KiB vanilla USA ROM and its clean-boot baseline.
coverage: verified
---

# USA release

This pack targets the USA release:

| Field | Value |
|---|---|
| Title | Final Fantasy Legend, The (USA) |
| Size | 131,072 bytes |
| SHA-1 | `901dfc83c72e172d35a376835807fc788444a9bb` |
| Mapper | MBC2 |

The source project's patched 256 KiB build is not the target. It has a different
ROM hash, a different bank layout, and different save-state compatibility.

The clean-boot baseline is about 900 frames of START/A mashing to the world map.
Save a state there and keep its sidecar. That state is the reproducible starting
point for walking and encounter harvests.

The USA names used in this pack come from the local guides and the ROM. They are
not guaranteed to match the Japanese release.
