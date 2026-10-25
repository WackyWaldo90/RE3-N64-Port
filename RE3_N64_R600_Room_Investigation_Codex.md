# RE3 N64 Port — Room R600 Investigation and Integration Notes

**Project:** Resident Evil 3: Nemesis (PS1 Europe) → Nintendo 64  
**Audience:** Codex, reverse-engineering contributors, asset-conversion pipeline  
**Prepared:** 2026-10-25  
**Status:** Strong working identification; final runtime verification outstanding

## Executive finding

The project's **169th extracted RDT is `R600.RDT`**, which contains **zero extracted SCA collision records** but is **not an empty file**. Evidence collected during the investigation supports classifying R600 as a **special scripted presentation scene associated with The Mercenaries reward sequence**, rather than assuming it is a universal blank room that loads every other room.

**Important evidence distinction:** The Mercenaries association is a **strong working identification**, not a demonstrated fact from an emulator trace. Earlier research reported a character-reference association with a police chief and a money-awarding girl, and a prior binary inspection reported three cameras and script sections. Those details should be independently reproduced against the source RDT and documented in machine-readable output before Codex marks the identification as verified. Do not infer that Brian Irons necessarily appears in this scene solely from a secondary reference.

## Source inventory and measurements

| Item | Current evidence | Confidence |
|---|---|---|
| Extracted room files | 169 RDTs in project inventory | High — project inventory |
| Exceptional RDT | `RDT/R600.RDT` | High — GitHub `.github/room_inventory.csv` |
| R600 file length | 114,648 bytes | High — project inventory |
| R600 SCA offset | 548 decimal (`0x224`) | High — project inventory |
| R600 SCA count | 0 | High — project inventory |
| Rooms with nonzero SCA | 168 | High — project inventory |
| Total extracted SCA records | 5,291 | High — project inventory/tests |
| R600 cameras | Three reported in prior investigation | **Reverify from raw RDT** |
| R600 init script | Reported at offset `0x47C` in prior investigation | **Reverify from raw RDT** |
| R600 purpose | Mercenaries-related scripted/reward scene | **Working hypothesis pending runtime trace** |
| Clothing Boutique | Reported room ID `R10F` | Verify against RDT map and in-game behavior |

Primary project repository: https://github.com/WackyWaldo90/RE3-N64-Port

Relevant repository paths observed:
- `.github/room_inventory.csv` — authoritative current extracted room inventory.
- `.github/collision_records.csv` — decoded SCA records.
- `.github/test_collision_audit.py` — assertions for 169 rooms / 5,291 collision records.
- `PHASE_A.md` — recovery/build audit and toolchain limitations.
- `.github/REPORT.md` — project milestone and source notes.

Source locations:
- Google Drive RE3 folder: https://drive.google.com/drive/folders/1_CJSbPlElT1ScldYqPJQGGi2ItQsBz9X (M93 RDT extraction and later milestone archives).
- Dropbox project subtree: `/Source/resident evil 64&ps1`, containing the European RE3 BIN/CUE, engineering guides, and emulator/tool sources.
- Original disc metadata previously reported: `Resident Evil 3 - Nemesis (Europe).bin` (712,491,360 bytes). This does **not** imply that the binary was mounted or executed in the current Codex environment.

## Why zero collision does not mean an empty loading room

RDT files can contain camera definitions, scripts, object references and other data even if no SCA collision records were decoded. `R600.RDT` has substantial file content (114,648 bytes). Therefore:

1. **Do not delete or skip R600** because SCA count is zero.
2. **Do not assume R600 is a universal loader** without tracing references and transition behavior in the PS1 executable.
3. **Do not assume R600 is playable** simply because it is an RDT.
4. Preserve all 169 RDTs in the conversion manifest, including special-purpose scenes.

## Codex task: conclusively determine R600's role

### 1. Recover the original bytes

Locate `R600.RDT` from the M93 extracted RDT archive or re-extract from the original PS1 BIN. Record SHA-256, exact byte length and provenance (archive member path, extraction script, source disc ID). If access fails, stop and report the missing byte source; do not substitute invented data.

### 2. Decode RDT structures

Use verified RE3/Biohazard 3 RDT layout definitions (compare available bio-lib / RE3 modding references). Generate `reports/r600_sections.json` containing section offsets, sizes, parser version and validation warnings. Specifically enumerate camera records, camera/background references, SCA, SCD init/main scripts, object/enemy entries, masks and other known sections. Validate every offset against the file size.

### 3. Disassemble and classify scripts

Disassemble init and main scripts using a verified BIO3 opcode table. List opcodes, control-flow edges, door/room transition destinations, actor spawns, reward/score/currency operations and external references. Do not infer script meaning from opcode bytes without a documented mapping. Produce `reports/r600_script_disassembly.txt`.

### 4. Search inbound references

Search all 169 RDT scripts and, if available, the PS1 executable for references to room ID `R600` (including encoded room/stage formats). Distinguish ordinary door transitions from game-mode launch/ending/cutscene transitions. Produce `reports/r600_inbound_references.csv` with source file, byte offset, decoded opcode and target.

### 5. Compare Mercenaries sequence

Run the original PS1 game in an available emulator and capture the Mercenaries reward/presentation sequence. Trace loaded room ID, camera changes, models and scripts. Confirm whether the active room is R600. Save logs and screenshots with exact emulator version and disc checksum. If no emulator is available, label this step **NOT RUN** rather than **PASS**.

### 6. Resolve the universal-loader theory

Trace at least three ordinary door transitions and one Mercenaries reward transition. If normal transitions do not enter R600, reject the universal-loader hypothesis. If they do, document precisely how and whether R600 is visible, transient or a resource container.

### 7. Final classification

Update `assets/rooms/room_manifest.csv` with `R600` and fields `role`, `collision_count`, `camera_count`, `script_status`, `render_status`, `confidence`, `evidence_path`. Allowed role values should include `normal_room`, `special_scene`, `cutscene`, `unused`, `loader`, `unknown`. Set `role=special_scene` and `confidence=provisional` until evidence passes the emulator trace.

## N64 implementation requirements

- Retain **all 169 RDT identities** in the room database.
- Convert the **168 collision-bearing rooms** using the existing R3SC/R3BK work, but keep collision-less scenes as valid entries.
- R600 may need cameras, backgrounds, character models, scripts and mode-specific logic even without a collision mesh.
- Include the Clothing Boutique (`R10F`, pending mapping verification) in the room-viewer checklist.
- Implement Phase B **all-room viewer** before gameplay completion; allow selecting every room, including special scenes, and display unsupported features explicitly.
- **FMVs last:** defer all FMV transcoding/packing until non-FMV ROM footprint is measured and a cartridge capacity budget is established.
- Avoid copying proprietary RE2 N64 engine code into the independent port; use RE2 N64 as a behavioral/technical reference.
- Never claim a bootable ROM, converted background or emulator pass without an actual build artifact and reproducible test log.

## Phase A prerequisite warning

The repository's `PHASE_A.md` reported that as of 2026-10-25 the N64 SDK/compiler and emulator were unavailable in that recovery environment; no bootable ROM had been built or emulated. Codex must recheck the current environment and not treat that earlier report as permanent, but must not silently mark Phase A complete.

## Acceptance criteria for closing the R600 mystery

- [ ] Original `R600.RDT` bytes recovered and hash recorded.
- [ ] Camera/script/collision sections parsed with validated bounds.
- [ ] Inbound references enumerated from other RDTs and executable where possible.
- [ ] Mercenaries reward scene traced and R600 room ID confirmed or disproved.
- [ ] Universal-loader hypothesis tested with ordinary transitions.
- [ ] `room_manifest.csv` updated with evidence-backed classification.
- [ ] R600 preserved in N64 asset pipeline and room viewer.

**Decision today:** Keep R600 as a provisional **Mercenaries-related special scene**. The zero-collision result is established; the exact function needs reproducible runtime or script evidence before being treated as conclusively proven.
