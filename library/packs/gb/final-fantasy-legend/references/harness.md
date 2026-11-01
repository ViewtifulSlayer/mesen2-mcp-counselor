---
title: Mesen harness
summary: Measured speed, batched walk-harvest shape, rewind, and state hygiene.
coverage: verified
---

# Mesen harness

Every number here was measured on Mesen2 MCP 0.5.2 and re-checked on 0.6.0. The
0.6.0 walker sustained about 1,035 fps over 11,080 frames, inside the 0.5.2
range. Treat the exact rates as machine-specific.

## Speed

- `play_input`, `run_until`, `advance_frame`, and `run_script` accept `turbo`.
  With turbo the emulator runs about 780-1140 fps, roughly 15x real time.
- The dominant cost is tool-call round trips, not emulation. A batched Lua script
  that advanced 60,000 frames, fought six battles, and logged them finished in 61
  seconds inside a single call.
- Turbo does not rescue a script that installs per-instruction memory callbacks.
  An exec trace ran at about 220 fps because the Lua callback was the bottleneck.

## Rewind

Rewind works with the rewind buffer enabled. A test jumped to a 10-second
checkpoint (2,340 frames back) and played forward to land exactly on the
requested frame. Granularity is 30 frames. `allowPartial` caps the jump when the
history is shorter than the request.

Use rewind instead of reloading a state when a short experiment goes wrong.

## Batched walk-harvest skeleton

The shape that worked:

```lua
local mt = emu.memType.gameboyMemory
local function rb(a) return emu.read(a, mt) end
local base = emu.getState()['frameCount']
local function rel() return emu.getState()['frameCount'] - base end

local phase = 'walk'
local dir = 'right'

-- Gate on the four party records, not on "varied bytes".
local function isBattle()
  if rb(0xD000) ~= 0x40 then return false end
  if rb(0xD020) ~= 0x40 or rb(0xD040) ~= 0x40 or rb(0xD060) ~= 0x40 then return false end
  local hp = rb(0xD003) + 256 * rb(0xD004)
  return hp > 0 and hp < 0x1000
end

emu.addEventCallback(function()
  if phase == 'walk' then
    emu.setInput({[dir] = true})
  else
    local m = rel() % 40
    if m < 4 then emu.setInput({down = true})
    elseif m < 20 then emu.setInput({})
    elseif m < 24 then emu.setInput({a = true})
    else emu.setInput({}) end
  end
end, emu.eventType.inputPolled)

emu.addEventCallback(function()
  local f = rel()
  local inBattle = isBattle()
  if phase == 'walk' and inBattle then
    emu.log('battle at ' .. f)
    phase = 'fight'
  elseif phase == 'fight' and not inBattle then
    phase = 'walk'
  end
  if f > 45000 then emu.setInput({}) emu.mcp.done() end
end, emu.eventType.endFrame)
```

Run it with `frames` slightly above the script's own limit and a generous
`timeoutMs`; the script stops itself with `emu.mcp.done()`.

Recipes load kits from `-- includes: <kit>`. Kit modules use `-- requires:` for
their own dependencies. Putting `-- requires:` in a recipe leaves the kit
unloaded.

## Probe discipline

- `$FFBD` is the current map's encounter id. Sample it every frame; log only
  changes. Each change is a map boundary.
- A frozen scroll axis means a map edge, not a wall. Check SCX and SCY separately
  before concluding a walker is stuck.
- `$D000` is scene-dependent. In the field it is the tilemap; in battle it is
  unit records. Use the four party records, not byte variety.
- Read `$FF00`-`$FFFF` through `emu.read` in Lua. `read_memory` returns `FF` for
  IO.

## State hygiene

`save_state_file` writes a `.json` sidecar with the ROM SHA-1.
`load_state_file` refuses a mismatched ROM by default. Keep the sidecar with the
state. Without it, `list_states` reports `valid: false` and you lose the ability
to prove which ROM the state belongs to.

The older `docs/savestates/` states have no sidecars and one 256 KiB state was
loaded against the 128 KiB image. Do not repeat that.

## Crashed states

A crashed state and a paused menu can look identical in a screenshot. Check for a
runaway before trusting one:

- PC stuck at `$00C9` with `haltCounter = 1`
- only a few hundred instructions per frame instead of roughly 17,000
- a WRAM checksum over `$C000-$DFFF` that does not move over 60 frames

If all three hold, the state is dead, not paused.
