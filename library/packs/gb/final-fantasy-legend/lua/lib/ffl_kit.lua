-- description: Final Fantasy Legend (GB) helpers: battle records, party HP, encounter id, and battle detection.
-- requires:
--
-- Usage (run_script includes=["ffl_kit"]):
--   ffl.record(slot)       -- 32-byte record at $D000 + slot*32
--   ffl.party()            -- slots 0..3
--   ffl.enemy()            -- slot 4
--   ffl.encounterId()      -- $FFBD
--   ffl.isBattle()         -- four $40 party records plus sane HP
--   ffl.describe(record)   -- one-line string

ffl = ffl or {}

local function mem()
  return emu.memType.gameboyMemory or emu.memType.gbWorkRam
end

function ffl.r8(address)
  return emu.read(address, mem())
end

function ffl.r16(address)
  return ffl.r8(address) + 256 * ffl.r8(address + 1)
end

function ffl.record(slot)
  local base = 0xD000 + slot * 32
  return {
    slot = slot,
    sprite = ffl.r8(base + 0),
    class = ffl.r8(base + 1),
    hp = ffl.r16(base + 3),
    maxHp = ffl.r16(base + 5),
    str = ffl.r8(base + 7),
    def = ffl.r8(base + 8),
    agi = ffl.r8(base + 9),
    mana = ffl.r8(base + 10),
    crtype = ffl.r8(base + 31),
  }
end

function ffl.party()
  return { ffl.record(0), ffl.record(1), ffl.record(2), ffl.record(3) }
end

function ffl.enemy()
  return ffl.record(4)
end

function ffl.encounterId()
  return ffl.r8(0xFFBD)
end

function ffl.isBattle()
  if ffl.r8(0xD000) ~= 0x40 then return false end
  if ffl.r8(0xD020) ~= 0x40 or ffl.r8(0xD040) ~= 0x40 or ffl.r8(0xD060) ~= 0x40 then
    return false
  end
  local hp = ffl.r16(0xD003)
  return hp > 0 and hp < 0x1000
end

function ffl.describe(record)
  return string.format(
    "slot=%d sprite=$%02X class=%d hp=%d/%d crtype=$%02X stats=%d/%d/%d/%d",
    record.slot, record.sprite, record.class, record.hp, record.maxHp,
    record.crtype, record.str, record.def, record.agi, record.mana
  )
end

function ffl.logState(prefix)
  emu.log(prefix .. " encounter=$" .. string.format("%02X", ffl.encounterId()))
  for _, record in ipairs(ffl.party()) do
    emu.log(prefix .. " party " .. ffl.describe(record))
  end
  emu.log(prefix .. " enemy " .. ffl.describe(ffl.enemy()))
end

return ffl
