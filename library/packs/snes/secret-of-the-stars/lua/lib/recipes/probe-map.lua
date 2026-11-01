-- includes: sots_kit
-- Print the 16-bit map id, 8-bit encounter id, battle flag, game state, and
-- both party slot ranges. The encounter id is the current or last encounter;
-- it is not cleared when the party returns to the field.

local result = {
  mapId = sots.mapId(),
  encounterId = sots.encounterId(),
  battleFlag = sots.battleFlag(),
  gameState = sots.gameState(),
  aqutallion = sots.aqutallionSlots(),
  kustera = sots.kusteraSlots(),
}

emu.log(string.format(
  "map=$%04X encounter=$%02X battleFlag=%d gameState=%d aq=%s kustera=%s",
  result.mapId, result.encounterId, result.battleFlag, result.gameState,
  table.concat(result.aqutallion, ","), table.concat(result.kustera, ",")
))

if emu.mcp and emu.mcp.result then
  emu.mcp.result(result)
end
if emu.mcp and emu.mcp.done then
  emu.mcp.done()
end
