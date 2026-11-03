#!/usr/bin/env python3
"""Build the pack's derived tables and provenance.

The rows are curated from the save tool's docs and the local build measurement.
This script does not read the save tool tree, so the CSVs are reproducible from
the pack alone. The source names and hashes in provenance.json record origin.

Run from the pack root:

    python tests/build_tables.py
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
DATA = PACK / "data"

SAVE_FIELDS = [
    ("root", "systemSaveData", "object", "-", "verified", "One system block per file: sfSys, systemData, configData", "SaveData.bin.json; save_layout.md 1"),
    ("root", "saveDataList", "array", "59", "verified", "Numbered save slots; count the array, not the marker literal", "fixture; save_layout.md 1"),
    ("root", "quickSaveData", "object", "1", "verified", "Independent quick snapshot, not a mirror of the active slot", "fixture; save_layout.md 1.1"),
    ("root", "autoSaveData", "object", "1", "verified", "Independent auto snapshot, not a mirror of the active slot", "fixture; save_layout.md 1.1"),
    ("slot", "saveItemInfoData", "object", "7 keys", "verified", "Cheap slot metadata for the picker", "fixture"),
    ("slot", "saveDataJsonStr", "string", "~68.6 KB", "verified", "Nested JSON string; requires a second JSON.parse", "fixture"),
    ("saveItemInfoData", "CharacterNumber", "number", "-", "verified", "Leader character ID; 5 = Asellus in slot 0", "fixture"),
    ("saveItemInfoData", "CharacterName", "string", "-", "verified", "Fullwidth Latin name; do not normalize away", "fixture"),
    ("saveItemInfoData", "MapNumber", "number", "-", "verified", "0-based area index, not a room ID", "fixture; save_layout.md 8.2"),
    ("saveItemInfoData", "PlayTimeHours", "number", "-", "verified", "Slot play time hours", "fixture"),
    ("saveItemInfoData", "PlayTimeMinutes", "number", "-", "verified", "Slot play time minutes", "fixture"),
    ("saveItemInfoData", "IsTakeover", "bool", "-", "observed", "NG+ carry-over marker (crown), not completion", "fixture; agent_state slot_flags"),
    ("saveItemInfoData", "RouteCharacterNumber", "number", "-", "observed", "Fuse route character; 5 = Asellus in the 2021 file", "fixture"),
    ("sfSys", "buf", "array[int8]", "24", "not mapped", "Raw system buffer", "save_layout.md 3.1"),
    ("sfSys", "name", "array[int8]", "16", "not mapped", "Name/key field", "save_layout.md 3.1"),
    ("sfSys", "chk", "array[int8]", "1", "integrity", "Checksum-like; algorithm unknown", "save_layout.md 3.1; runbook 7"),
    ("sfSys", "chk2", "array[int8]", "3", "integrity", "Checksum-like; algorithm unknown", "save_layout.md 3.1; runbook 7"),
    ("sfSys", "chk3", "array[int8]", "3", "integrity", "Checksum-like; algorithm unknown", "save_layout.md 3.1; runbook 7"),
    ("sfSys", "chk4", "array[int8]", "2", "integrity", "Checksum-like; algorithm unknown", "save_layout.md 3.1; runbook 7"),
    ("sfSys", "blood", "number", "-", "observed", "Questionnaire blood type; no verified effect", "save_layout.md 3.1"),
    ("sfSys", "seiza", "number", "-", "observed", "Questionnaire zodiac; no verified effect", "save_layout.md 3.1"),
    ("sfSys", "learning", "array", "8", "not mapped", "Unknown", "save_layout.md 3.1"),
    ("sfSys", "parLev", "number", "-", "observed", "New-scenario starting Battle Rank; 0 no clear, 33 post-clear", "save_layout.md 3.1; runbook 4.11"),
    ("sfSys", "start", "array", "9", "observed", "Per-hero scenario start count", "runbook completion_record"),
    ("sfSys", "end", "array", "9", "observed", "Per-hero clear count", "runbook completion_record"),
    ("sfSys", "end2", "array", "9", "observed", "Per-hero true-ending count", "runbook completion_record"),
    ("sfSys", "id", "array", "32", "not mapped", "Unknown", "save_layout.md 3.1"),
    ("sfSys", "fill", "array", "23", "not mapped", "Padding or unknown", "save_layout.md 3.1"),
    ("sfSys", "sum", "array", "1", "integrity", "Checksum-like; algorithm unknown", "save_layout.md 3.1"),
    ("systemData", "clearFlag", "array", "16", "verified", "HERO-indexed clear flags; 3 Fuse, 5 Asellus", "save_layout.md 3.2"),
    ("systemData", "joinedFlag", "array", "41", "observed", "All false with a one-member party; not the active roster", "save_layout.md 3.2"),
    ("systemData", "enterRegionFlag", "array", "31", "observed", "Region-entry flags; index map unmapped", "save_layout.md 3.2"),
    ("systemData", "mapIntroFlag", "array", "9", "observed", "Map-intro flags; index map unmapped", "save_layout.md 3.2"),
    ("systemData", "endingFlag", "array", "17", "verified", "ENDING-indexed; 6 Asellus half, 14 Fuse Asellus", "save_layout.md 3.2"),
    ("systemData", "isFuseAppearance", "bool", "-", "observed", "Fuse appearance state", "runbook completion_record"),
    ("systemData", "totalFuseBossNum", "array", "8", "observed", "Fuse boss counts; all zero in the 2021 file", "runbook completion_record"),
    ("systemData", "totalFuseRootStart", "array", "8", "observed", "Fuse route starts; index 4 inferred Asellus", "runbook completion_record"),
    ("systemData", "totalFuseRootClear", "array", "8", "observed", "Fuse route clears; index 4 inferred Asellus", "runbook completion_record"),
    ("systemData", "saveDataIndex", "number", "-", "observed", "Active slot index in saveDataList", "runbook completion_record"),
    ("systemData", "shopRecordList", "array", "17", "verified", "Purchase ledger of fixed stock tables, not visited shops", "save_layout.md 3.2"),
    ("systemData", "goldSaleMoney", "number", "-", "observed", "Gold sale money", "save_layout.md 3.2"),
    ("configData", "language", "number/string", "-", "observed", "Display language selector; values not decoded", "save_layout.md 3.3"),
    ("configData", "isEnableAutoSave", "bool", "-", "observed", "Auto-save toggle", "save_layout.md 3.3"),
    ("configData", "padKeyconfigData", "object", "-", "observed", "Pad input mapping; keycodes not decoded", "save_layout.md 3.3"),
    ("configData", "keyboardKeyconfigData", "object", "-", "observed", "Keyboard input mapping; keycodes not decoded", "save_layout.md 3.3"),
    ("inner", "ply", "array", "41", "verified", "One record per character; presence is not party membership", "fixture; save_layout.md 6"),
    ("pty", "psnCnt", "number", "-", "verified", "Active party count; 1 in slot 0", "fixture"),
    ("pty", "heroNo", "number", "-", "verified", "Leader character ID; 5 in slot 0", "fixture"),
    ("pty", "chrNo", "array", "56", "verified", "Roster order; 255 padded", "fixture"),
    ("pty", "companionChrNo", "array", "56", "verified", "Companion list; 255 padded", "fixture"),
    ("pty", "team", "array", "56", "verified", "Active party order; 255 padded", "fixture"),
    ("pty", "money", "number", "-", "verified", "Party money; 100 in slot 0", "fixture"),
    ("pty", "item_a", "array", "257", "verified", "Inventory entries {itemNo,itemCnt}; empty 255/0", "fixture; save_layout.md 5.2"),
    ("pty", "snroFlg", "array", "512", "observed", "Scenario flags; mix of bit fields and counters", "save_layout.md 5.3"),
    ("pty", "boxFlg", "array", "64", "not mapped", "All zero in slot 0", "save_layout.md 5.3"),
    ("pty", "scenarioChartStateArray", "array", "1024", "partial", "Indices 157/158 map to Asellus chart labels; set-value meaning unknown", "save_layout.md 5.3"),
    ("pty", "event_btl", "array", "16", "observed", "All zero in slot 0", "save_layout.md 5.3"),
    ("pty", "cfg1", "array", "12", "observed", "Order list, likely", "save_layout.md 5.3"),
    ("pty.each", "parLev", "number", "-", "observed", "Packed Battle Rank Points; 16 points per rank", "save_layout.md 5.5; runbook 4.11"),
    ("pty.each", "combo_", "array", "40", "not mapped", "65535 empty", "save_layout.md 5.5"),
    ("pty", "time", "number", "-", "observed", "Tick clock shared with eventwk.counter", "save_layout.md 7.1"),
    ("eventwk", "mapNo", "number", "-", "verified", "Previous map ID, not the current room", "fixture; save_layout.md 8.1"),
    ("eventwk", "xpos", "number", "-", "verified", "Player X position", "fixture"),
    ("eventwk", "zpos", "number", "-", "verified", "Player Z position", "fixture"),
    ("eventwk", "counter", "number", "-", "observed", "Tick clock; difference from pty.time is constant per map", "save_layout.md 7.1"),
    ("eventwk", "wk", "array", "32", "not mapped", "Sparse, no mapping", "save_layout.md 7"),
    ("eventwk", "temp", "array", "256", "observed", "temp[192] = additional-content mode (1 on, 0 off); rest unmapped", "save_layout.md 7; agent_state slot_flags"),
    ("mapwk", "map_name", "number", "-", "verified", "0-based area index; 26 = Chateau Aiguille", "fixture; save_layout.md 8.2"),
    ("mapwk", "region_no", "number", "-", "observed", "Region number", "save_layout.md 8"),
    ("mapwk", "imfName", "string", "-", "verified", "Current room asset name, e.g. imf303 = 771", "fixture; save_layout.md 8.1"),
    ("mapwk", "Value4", "number", "-", "verified", "Duplicate of the current room ID", "fixture; save_layout.md 8.1"),
    ("mapwk", "obj", "array", "64", "not mapped", "Fixed capacity; only obj_cnt entries live", "save_layout.md 8"),
    ("mapwk", "vx", "number", "-", "observed", "View X", "save_layout.md 8"),
    ("mapwk", "vy", "number", "-", "observed", "View Y", "save_layout.md 8"),
    ("mapwk", "vz", "number", "-", "observed", "View Z", "save_layout.md 8"),
    ("ply[]", "hpMax", "number", "-", "verified", "Maximum HP only; no current-HP field", "save_layout.md 6; runbook 4.2"),
    ("ply[]", "lpNow", "number", "-", "verified", "Current LP", "fixture"),
    ("ply[]", "race", "number", "byte 0x16", "verified", "Race/gender code", "save_layout.md 6"),
    ("ply[]", "nature", "number", "byte 0x15", "verified", "Gifts bitfield", "save_layout.md 6"),
    ("ply[]", "getType", "number", "byte 0x17", "not mapped", "No glossary; values 0-11 seen", "save_layout.md 6"),
    ("ply[]", "getskill", "array", "64", "verified", "Ability bit grid; MSB-first; ability=(byte-0x38)*8+bit", "runbook 4.2"),
    ("ply[]", "eqpAtk", "array", "8", "verified", "Equipped arts; 65535 empty", "fixture"),
    ("ply[]", "eqpItm", "array", "8", "verified", "Equipped items; 255 empty", "fixture"),
    ("ply[]", "tribial_work", "array", "16", "partial", "Race scratch: Mec data[0]/[2], Monster data[0], Mystic data[4..12]", "save_layout.md 6"),
    ("ply[]", "mPart", "number", "-", "not mapped", "240 on all but one record", "save_layout.md 6"),
    ("ply[]", "allLpLoss", "bool", "-", "observed", "All-LP-loss flag", "save_layout.md 6"),
    ("pty", "parLev", "missing", "-", "do not use", "Phantom path; the live value is pty.each.parLev", "save_layout.md 5.6"),
]

SENTINELS = [
    ("Empty character ID", "255", "8-bit", "chrNo, companionChrNo, team, itemNo, eqpItm"),
    ("Empty item ID", "255", "8-bit", "item_a[].itemNo"),
    ("Empty equipment attack slot", "65535", "16-bit", "eqpAtk[]"),
    ("Empty equipment item slot", "255", "8-bit", "eqpItm[]"),
    ("Empty combo entry", "65535", "16-bit", "pty.each.combo_[]"),
    ("Character-array padding", "255", "8-bit", "all three 56-length party arrays"),
    ("Empty inventory entry", "{itemNo:255,itemCnt:0}", "pair", "item_a[]"),
    ("Enemy NotUse", "255", "8-bit", "enemy/form table; 255 is not a real absorb"),
    ("Missing key-item range", "0xF0-0xFF", "16 ids", "not equippable; item stats omit them"),
]

ID_NAMESPACES = [
    ("item", "0xNN", "0x00-0xFF", "256", "asset", "resources.assets item table @ 7,738,252", "16-byte padded ASCII; 248 named, NotUse placeholders"),
    ("character", "0xNN", "0x00-0x3F", "64", "asset", "resources.assets character table @ 7,783,498", "16-byte records; save can carry 0x40 unmapped"),
    ("area", "0xNN", "0x00-0x44", "69", "asset", "resources.assets area table @ 7,782,118", "20-byte records; 0-based; 26 Chateau Aiguille"),
    ("ability", "0x000-0x1FF", "0-511", "512", "documented", "ability_names.json; char_record_layout.json", "7 ambiguous names; 8 school blocks"),
    ("map/room", "0x000-0x4B9", "22-1209", "869", "community", "maps.json; IMF_File_Names.txt", "319 gaps; 425 is a gap"),
    ("enemy/form", "0x00-0xFF", "0-255", "256", "documented", "monster_forms.json; mystic_absorbs.json", "form names are documented, not all observed"),
    ("shop type", "decimal", "0-90", "17", "documented", "shop_names.json", "labels by stock location; gold split medium"),
    ("scenario/hero", "0-8", "0-8", "9", "documented", "SystemData.HERO", "Emelia, Lute, Red, Fuse, Blue, Asellus, T260G, Riki, Rouge"),
    ("ending", "0-16", "0-16", "17", "documented", "SystemData.ENDING", "0-9 named; 10-16 Fuse endings"),
    ("element flag", "code", "14 flags", "14", "documented", "ability_names.json meta.element_legend", "S,P,B,H,C,E,F,X,Gr,Gz,So,Wa,Th,AA"),
    ("init set", "1-4", "1-4", "4", "documented", "init_sets.json", "selected by last-clear Battle Rank"),
]

UNITY_BUILD = [
    ("executable", "SaGa Frontier Remastered.exe", "884376", "ee5791abda515de0509530a2e719cae08958865120bb201c2fc905ea94f6baee"),
    ("unity_player", "UnityPlayer.dll", "25957808", "f015940f30f981c29d9e937085cb39866152bc6c0e07c6d927e3a3e40a52dec1"),
    ("game_assembly", "GameAssembly.dll", "37480960", "f157541f60fbf9824464968fc2b1545d7a15f59a06e39aae9c573fd9cedaa1ce"),
    ("il2cpp_metadata", "SaGa Frontier Remastered_Data/il2cpp_data/Metadata/global-metadata.dat", "8165108", "c58d2e1464b3abb55577a95807adcc2864c1ea1a57210ae73d8541756c0c5ff6"),
    ("global_managers", "SaGa Frontier Remastered_Data/globalgamemanagers", "2632172", "2b247e4b4b17f52d104126600a160ab04d8299c6c62c638a133e77829cbdb443"),
    ("resources_assets", "SaGa Frontier Remastered_Data/resources.assets", "144872176", "1d99d8d8f6802cc6e3a04f45fda7c421ca0aa0d50259641bc70b379aa586591f"),
]

KNOWN_GAPS = [
    ("integrity", "sfSys.chk", "No known algorithm; no checksum fixer for this title", "Hook the game's save write and compare inputs/outputs", "integrity"),
    ("integrity", "sfSys.chk2", "Same as chk", "Hook the save write", "integrity"),
    ("integrity", "sfSys.chk3", "Same as chk", "Hook the save write", "integrity"),
    ("integrity", "sfSys.chk4", "Same as chk", "Hook the save write", "integrity"),
    ("integrity", "sfSys.sum", "Same as chk", "Hook the save write", "integrity"),
    ("integrity", "pty.sum", "Same as chk", "Hook the save write", "integrity"),
    ("character", "getType (0x17)", "No glossary; values 0-11 seen", "Controlled save diffs", "not mapped"),
    ("character", "tribial_work remaining bytes", "Only the Mec/Monster/Mystic subsets are mapped", "Progression diffs", "partial"),
    ("character", "mPart", "240 on all but one record", "Controlled save diffs", "not mapped"),
    ("flags", "boxFlg", "All zero in slot 0", "Trigger events and diff", "not mapped"),
    ("flags", "eventwk.wk", "Sparse, no mapping", "Trigger events and diff", "not mapped"),
    ("flags", "eventwk.temp except 192", "Only 192 is mapped", "Trigger events and diff", "observed"),
    ("flags", "snroFlg 343 bytes", "169 named, 343 unnamed", "Extend the dictionary or hook writes", "observed"),
    ("map", "mapwk.obj[]", "Struct array undecoded", "Compare maps", "not mapped"),
    ("map", "room 0x1A9 (425)", "Gap in the community map table", "Find a save in the room", "verified"),
    ("area", "current vs scenario-start", "No fixture crosses areas", "Post-area-change save", "unverified"),
    ("init", "INIT 3 (BR 4-6)", "No BR 4-6 clear fixture", "Controlled clear or live bridge", "unverified"),
    ("completion", "last-clear rank", "Not sfSys.parLev", "Hook the save write at clear", "unverified"),
    ("fuse", "Fuse routes 0-3, 5-7", "One fixture; index 4 inferred Asellus", "Second route fixture", "partial"),
    ("character", "chrNo 0x40", "No name-table entry", "Asset search or live inspection", "unmapped"),
]

TABLES = [
    ("runtime", "Name tables", "docs/constants.json", "64 characters, 256 items, 69 areas", "asset", "resources.assets fixed-width tables", "tests/sfr_save_tool/extract_name_tables.js", "Offsets 7,738,252 / 7,783,498 / 7,782,118"),
    ("runtime", "Ability names", "docs/ability_names.json", "512", "documented", "gameinfo/json/abilities.json; ability_elements.htm", "tests/sfr_save_tool/build_gameinfo.py", "14 element flags; 7 ambiguous names"),
    ("runtime", "Flag names", "docs/flag_names.json", "169 bytes, 440 bits, 345 states", "documented", "gameinfo/discord/bf386d29fa5f29d5.txt", "tests/sfr_save_tool/build_flags.py", "CP932 source; 169 named of 512 bytes"),
    ("runtime", "Flag glosses", "docs/flag_meanings_en.json", "710 meanings, 167 blocks", "draft", "flag_names.json; reviewed TSV batches", "tests/sfr_save_tool/build_flag_translations.py", "Unofficial English gloss"),
    ("runtime", "INIT sets", "docs/init_sets.json", "4 sets, 158 records", "documented", "gameinfo/json/characters_init.json", "tests/sfr_save_tool/build_init_sets.py", "INIT 3 unobserved"),
    ("runtime", "Mec item stats", "docs/item_stats.json", "240", "documented", "Data Mechanics Guide [ITEMD03]", "tests/sfr_save_tool/build_item_stats.py", "0x00-0xEF; Mec column only"),
    ("runtime", "Map names", "docs/map_names.json", "869", "community", "gameinfo/json/maps.json; IMF_File_Names.txt", "tests/sfr_save_tool/build_gameinfo.py", "319 gaps; one reviewed correction"),
    ("runtime", "Monster forms", "docs/monster_forms.json", "256 forms, 120 targets", "documented", "Data Mechanics Guide transformation tables", "tests/sfr_save_tool/build_monster_forms.py", "13 Table 1 targets (16 rows) + 107 Table 2 targets (128 rows)"),
    ("runtime", "Monster lab", "docs/monster_lab.json", "134 abilities, 88 form-stat entries", "documented", "Data Mechanics Guide; Oulak blocks", "tests/sfr_save_tool/build_monster_lab.py", "86 Oulak blocks; Space Magic is Head but cannot satisfy"),
    ("runtime", "Mystic absorbs", "docs/mystic_absorbs.json", "256 enemies, 465 slots", "documented", "Data Mechanics Guide [MYSAB02]", "tests/sfr_save_tool/build_mystic_absorbs.py", "160 enemies with arts"),
    ("runtime", "Shop labels", "docs/shop_names.json", "17", "documented", "Essence of SaGa item-selling page; Steam grouping", "manual label review", "Location + stock, not in-game names"),
    ("source", "Gameinfo manifest", "docs/gameinfo/json/manifest.json", "512 abilities, 256 items, 869 maps", "generated", "community sources", "tests/sfr_save_tool/build_gameinfo.py", "Source hashes and counts"),
    ("source", "INIT characters", "docs/gameinfo/json/characters_init.json", "40 x 4", "generated", "INITDATA, INI2DATA, INI3DATA, INI4DATA", "tests/sfr_save_tool/build_gameinfo.py", "Four sets; source defects recorded"),
    ("source", "Character layout", "docs/gameinfo/json/char_record_layout.json", "256-byte layout + 512-bit grid", "generated", "char_status.txt", "tests/sfr_save_tool/build_gameinfo.py", "60 recorded grid defects"),
    ("source", "Abilities", "docs/gameinfo/json/abilities.json", "512", "generated", "PS1 ability structs + element flags", "tests/sfr_save_tool/build_gameinfo.py", "505/512 struct agreement"),
    ("source", "Items", "docs/gameinfo/json/items.json", "256", "generated", "PS1 item structs + asset names", "tests/sfr_save_tool/build_gameinfo.py", "242/256 name agreement"),
    ("source", "Maps", "docs/gameinfo/json/maps.json", "869", "generated", "community map list + IMF names", "tests/sfr_save_tool/build_gameinfo.py", "One reviewed correction"),
    ("source", "Guide sections", "docs/gameinfo/json/mechanics_guide_sections.json", "186 sections", "generated", "Data Mechanics Guide", "tests/sfr_save_tool/build_gameinfo.py", "Section index; no guide text"),
]


def write_csv(name: str, header: list[str], rows: list[tuple[str, ...]]) -> Path:
    path = DATA / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    files = {}
    files["data/save-fields.csv"] = write_csv(
        "save-fields.csv",
        ["area", "path", "type", "length", "status", "meaning", "evidence"],
        SAVE_FIELDS,
    )
    files["data/sentinels.csv"] = write_csv(
        "sentinels.csv",
        ["meaning", "value", "width", "notes"],
        SENTINELS,
    )
    files["data/id-namespaces.csv"] = write_csv(
        "id-namespaces.csv",
        ["namespace", "key_format", "range", "count", "status", "source", "notes"],
        ID_NAMESPACES,
    )
    files["data/unity-build.csv"] = write_csv(
        "unity-build.csv",
        ["role", "path", "bytes", "sha256"],
        UNITY_BUILD,
    )
    files["data/known-gaps.csv"] = write_csv(
        "known-gaps.csv",
        ["area", "field", "why_blocked", "next_test", "status"],
        KNOWN_GAPS,
    )
    files["data/tables-inventory.csv"] = write_csv(
        "tables-inventory.csv",
        ["kind", "table", "file", "records", "status", "source", "generator", "notes"],
        TABLES,
    )

    provenance = {
        "schemaVersion": 1,
        "tables": [
            {
                "file": "data/save-fields.csv",
                "origin": "source",
                "source": "Save tool docs: save_layout.md sections 1-9, project_runbook.md sections 3-4, and the fixture assertions.",
                "generator": "tests/build_tables.py",
                "sha256": digest(files["data/save-fields.csv"]),
                "verifiedOn": "2026-11-03",
                "notes": "Field inventory with status and evidence. 87 rows; no field is invented.",
            },
            {
                "file": "data/sentinels.csv",
                "origin": "source",
                "source": "Save tool docs: save_layout.md section 9.",
                "generator": "tests/build_tables.py",
                "sha256": digest(files["data/sentinels.csv"]),
                "verifiedOn": "2026-11-03",
                "notes": "Empty and padding values used by the save.",
            },
            {
                "file": "data/id-namespaces.csv",
                "origin": "source",
                "source": "Save tool runtime tables and docs/gameinfo/json/manifest.json.",
                "generator": "tests/build_tables.py",
                "sha256": digest(files["data/id-namespaces.csv"]),
                "verifiedOn": "2026-11-03",
                "notes": "Ranges and counts; names stay in the runtime tables.",
            },
            {
                "file": "data/unity-build.csv",
                "origin": "observation",
                "source": "Local SaGa Frontier Remastered install, measured 2026-11-03.",
                "generator": "tests/build_tables.py",
                "sha256": digest(files["data/unity-build.csv"]),
                "verifiedOn": "2026-11-03",
                "notes": "Six SHA-256 values that pin the build. No binaries are included.",
            },
            {
                "file": "data/known-gaps.csv",
                "origin": "source",
                "source": "Save tool docs: save_layout.md section 11 and agent_state.json next_session.",
                "generator": "tests/build_tables.py",
                "sha256": digest(files["data/known-gaps.csv"]),
                "verifiedOn": "2026-11-03",
                "notes": "Each gap names the next test; open questions are not presented as answers.",
            },
            {
                "file": "data/tables-inventory.csv",
                "origin": "source",
                "source": "Save tool runtime tables, their generators, and docs/gameinfo/json/manifest.json.",
                "generator": "tests/build_tables.py",
                "sha256": digest(files["data/tables-inventory.csv"]),
                "verifiedOn": "2026-11-03",
                "notes": "11 runtime tables and 7 gameinfo source datasets.",
            },
        ],
    }
    (DATA / "provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {len(files)} CSV tables and data/provenance.json")
    for name, path in files.items():
        print(f"  {name}: {len(path.read_text(encoding='utf-8').splitlines()) - 1} rows, {digest(path)[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
