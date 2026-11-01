-- description: Secret of the Stars (SNES) helpers for verified RAM probes.
-- requires:
--
-- Verified on Mesen2 MCP 0.6.0 against the USA ROM
-- (SHA-1 958a0a835e2e39f382cb37a99098a3cdd4812cf7) on 2026-11-01.
--
-- Usage (run_recipe includes=["sots_kit"]):
--   sots.state()               -- battle flag, game state, map/encounter, parties, battle pools
--   sots.mapId()               -- 16-bit $040E
--   sots.encounterId()         -- 8-bit $043C; last encounter, not cleared on the field
--   sots.aqutallionSlots()     -- $04A4..$04A8
--   sots.kusteraSlots()        -- $04A9..$04AD
--   sots.kusteraSize()         -- $04BD
--   sots.battleGold()          -- $0D1F, battle pool only
--   sots.battleEp()            -- $0D21, battle pool only
--   sots.hero(index, offset)   -- byte at $5000 + index * $36 + offset
--   sots.hero0(offset)         -- shortcut for hero 0
--   sots.heroName(index)       -- seven-byte name, 0x40 + ASCII, FF-terminated
--   sots.spells(index)         -- the seven spell bytes at +$26..+$2C
--
-- $0D1F and $0D21 are battle pools, not the save's total gold. They read 0 on
-- the field and keep the last battle's values after victory. The encounter id
-- also keeps the last battle's value after returning to the field.

sots = sots or {}

sots.heroStride = 0x36

local function mem()
  return emu.memType.snesWorkRam or emu.memType.workRam
end

function sots.r8(address)
  return emu.read(address, mem())
end

function sots.r16(address)
  return sots.r8(address) + 256 * sots.r8(address + 1)
end

function sots.battleFlag()
  return sots.r8(0x0020)
end

function sots.gameState()
  return sots.r8(0x0053)
end

function sots.mapId()
  return sots.r16(0x040E)
end

function sots.encounterId()
  return sots.r8(0x043C)
end

function sots.aqutallionSlots()
  local slots = {}
  for index = 0, 4 do slots[#slots + 1] = sots.r8(0x04A4 + index) end
  return slots
end

function sots.kusteraSlots()
  local slots = {}
  for index = 0, 4 do slots[#slots + 1] = sots.r8(0x04A9 + index) end
  return slots
end

function sots.kusteraSize()
  return sots.r8(0x04BD)
end

function sots.battleGold()
  return sots.r16(0x0D1F)
end

function sots.battleEp()
  return sots.r16(0x0D21)
end

-- Legacy names. Both read the battle pool, not the save's total gold.
sots.gold = sots.battleGold
sots.ep = sots.battleEp

function sots.hero(index, offset)
  return sots.r8(0x5000 + index * sots.heroStride + offset)
end

function sots.hero0(offset)
  return sots.hero(0, offset)
end

function sots.heroName(index)
  local letters = {}
  for offset = 0, 6 do
    local value = sots.hero(index, offset)
    if value == 0xFF then break end
    if value >= 0x40 then
      letters[#letters + 1] = string.char(value - 0x40)
    end
  end
  return table.concat(letters)
end

function sots.spells(index)
  local spells = {}
  for offset = 0x26, 0x2C do
    spells[#spells + 1] = sots.hero(index, offset)
  end
  return spells
end

function sots.heroSummary(index)
  local rank = sots.hero(index, 0x07)
  return {
    name = sots.heroName(index),
    rank = rank,
    class = rank,
    level = sots.hero(index, 0x08),
    hp = sots.hero(index, 0x0F) + 256 * sots.hero(index, 0x10),
    maxHp = sots.hero(index, 0x11) + 256 * sots.hero(index, 0x12),
    mp = sots.hero(index, 0x13) + 256 * sots.hero(index, 0x14),
    maxMp = sots.hero(index, 0x15) + 256 * sots.hero(index, 0x16),
    power = sots.hero(index, 0x17) + 256 * sots.hero(index, 0x18),
    defense = sots.hero(index, 0x19) + 256 * sots.hero(index, 0x1A),
    speed = sots.hero(index, 0x1B) + 256 * sots.hero(index, 0x1C),
    luck = sots.hero(index, 0x1D) + 256 * sots.hero(index, 0x1E),
    condition = sots.hero(index, 0x1F),
    spells = sots.spells(index),
  }
end

function sots.hero0Summary()
  return sots.heroSummary(0)
end

function sots.state()
  return {
    battleFlag = sots.battleFlag(),
    gameState = sots.gameState(),
    mapId = sots.mapId(),
    encounterId = sots.encounterId(),
    aqutallion = sots.aqutallionSlots(),
    kustera = sots.kusteraSlots(),
    kusteraSize = sots.kusteraSize(),
    battleGold = sots.battleGold(),
    battleEp = sots.battleEp(),
    hero0 = sots.hero0Summary(),
  }
end

function sots.describe(state)
  return string.format(
    "battleFlag=%d gameState=%d map=$%04X encounter=$%02X battleGold=%d battleEp=%d " ..
    "aq=%s kustera=%s",
    state.battleFlag, state.gameState, state.mapId, state.encounterId,
    state.battleGold, state.battleEp,
    table.concat(state.aqutallion, ","), table.concat(state.kustera, ",")
  )
end

return sots
