-- includes: ffl_kit
-- frames: 1
-- Verify that the game is in the field (not a battle or a dead state) and
-- report the current encounter id. Party HP is reported only in battle.
--
-- This recipe does not walk. Use it after the documented clean-boot route or
-- after loading a known field state. If inBattle is true, the state is not a
-- field baseline.

local inBattle = ffl.isBattle()
local hp = {}
if inBattle then
  -- In the field, $D000 is the tilemap, so party records are only meaningful
  -- once the battle gate is true.
  for _, record in ipairs(ffl.party()) do
    hp[#hp + 1] = record.hp
  end
end

local result = {
  field = not inBattle,
  encounter = ffl.encounterId(),
  partyHp = hp,
}

emu.log("field=" .. tostring(result.field) ..
        " encounter=$" .. string.format("%02X", result.encounter) ..
        " partyHp=" .. table.concat(hp, ","))

if emu.mcp and emu.mcp.result then
  emu.mcp.result(result)
end
if emu.mcp and emu.mcp.done then
  emu.mcp.done()
end
