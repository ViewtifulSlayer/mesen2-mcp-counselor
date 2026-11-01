-- includes: sots_kit
-- Dump the verified battle, map, party, battle-pool, and hero-0 state.
-- $0D1F/$0D21 are battle pools; they read 0 on the field even when the save
-- has money. The encounter id keeps the last battle's value on the field.

local state = sots.state()

emu.log(sots.describe(state))
emu.log(string.format(
  "hero0 name=%s rank=%d level=%d hp=%d/%d mp=%d/%d power=%d defense=%d speed=%d luck=%d condition=$%02X",
  state.hero0.name, state.hero0.rank, state.hero0.level, state.hero0.hp, state.hero0.maxHp,
  state.hero0.mp, state.hero0.maxMp, state.hero0.power, state.hero0.defense,
  state.hero0.speed, state.hero0.luck, state.hero0.condition
))
emu.log("hero0 spells=" .. table.concat(state.hero0.spells, ","))

if emu.mcp and emu.mcp.result then
  emu.mcp.result(state)
end
if emu.mcp and emu.mcp.done then
  emu.mcp.done()
end
