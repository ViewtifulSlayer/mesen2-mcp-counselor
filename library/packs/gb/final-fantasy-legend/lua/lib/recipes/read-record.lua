-- includes: ffl_kit
-- frames: 1
-- Dump the current party, enemy, encounter id, and battle gate.
-- Run after a battle starts, or at any time to see the field state.

local result = {
  encounter = ffl.encounterId(),
  inBattle = ffl.isBattle(),
  party = ffl.party(),
  enemy = ffl.enemy(),
}

for _, record in ipairs(result.party) do
  emu.log("party " .. ffl.describe(record))
end
emu.log("enemy " .. ffl.describe(result.enemy))
emu.log("encounter $" .. string.format("%02X", result.encounter) ..
        " inBattle=" .. tostring(result.inBattle))

if emu.mcp and emu.mcp.result then
  emu.mcp.result(result)
end
if emu.mcp and emu.mcp.done then
  emu.mcp.done()
end
