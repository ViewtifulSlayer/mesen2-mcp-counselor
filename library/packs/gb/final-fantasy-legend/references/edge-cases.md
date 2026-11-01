---
title: Edge cases
summary: The expensive traps: invisible menu row, scene-dependent records, IO reads, and dead states.
coverage: verified
---

# Edge cases

## The invisible `ABIL` row

The battle menu draws `FIGHT` / `ABIL` / `RUN`, but `ABIL` is invisible. The hand
appears on `FIGHT` while the selection is on `ABIL`. A on a non-caster opens an
empty window that cannot be confirmed. B backs out; DOWN + A flees.

If a battle looks frozen after A, this is the first thing to check.

## `$D000` is scene-dependent

In battle, `$D000` is 32-byte unit records. In the field it is the tilemap. In
Base Town the tilemap happened to be one repeated id, so a "distinct bytes" test
worked; east of the river the tilemap is varied and the same test produced 198
false battles in ten seconds.

Gate on all four party records:

```
$D000 == $40, $D020 == $40, $D040 == $40, $D060 == $40
```

plus a sane HP. Do not gate on "varied bytes."

## Recipe headers

A recipe loads its kit with `-- includes: ffl_kit`. `-- requires:` is a kit
module header, not a recipe header. A recipe with `-- requires:` runs without
`ffl` and fails at the first reference. The 0.6.0 field test caught this; both
packs now use `-- includes:`.

## IO reads and breakpoints

- `read_memory` over `$FF00-$FFFF` returns `FF` for IO. Use `emu.read` from Lua.
- Read breakpoints on IO never fire. A watch on `$FF00` or `$FF44` recorded zero
  hits over ten frames while the LY-wait loop at `$00C7` was running every frame.
  Exec breakpoints are fine.
- Do not conclude "input is broken" from a silent IO read breakpoint.

## `emu.getState()['ppu.ly']` is not live

It reads 144 forever, even right after a fresh boot. Use a WRAM checksum or a
screenshot for liveness.

## Input API

`emu.setInput` takes the button table only:

```lua
emu.setInput({a = true})
```

Passing a port first raises `table expected, got number`. Input overrides set
from an `endFrame` callback do nothing; set them from an `inputPolled` callback.

`emu.write` to IO is ignored, the same as `$2000` for the MBC register. Drive
state through CPU writes or let the game do it.

## The class nibble

`+1` in a built record is the class nibble from `$71F0`, not the HP index and not
an HP mask. The first three confirmed monsters make `1 << (hpIndex + 1)` look
plausible; ALBATROS has HP index 0 and `+1 = 0`. Index the table with the crtype
id.

## Map edges

A pinned scroll axis means the map is one screen tall, not that the walker is
stuck. The east-bank forest pins SCY at `0` and sweeps SCX. Pushing south hits
the edge; the exits are east/west.

The BG tilemap at `$9800` is a repeating metatile texture, not a path map. Do
not BFS the screen from VRAM on this ROM; it can look blank while the screen is
full of trees.

## Dead states

A state can render a normal-looking battle pose while the CPU is running away
through data. Check PC, instructions per frame, and a WRAM checksum before
trusting it. A state that does not move over 60 frames is dead, not paused.

## Save-state sidecars

Keep the `.json` sidecar with a state. Without it, the ROM binding is lost and a
256 KiB state can be loaded against the 128 KiB image. The ROM hash is part of
the test, not an optional detail.
