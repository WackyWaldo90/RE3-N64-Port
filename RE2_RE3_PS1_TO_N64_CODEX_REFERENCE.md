# Resident Evil 2 / Resident Evil 3 — PS1-to-N64 Engineering Reference for Codex

**Edition:** 2026-10-25 | **Format:** UTF-8 Markdown | **Purpose:** Offline-first engineering handbook with source URLs, investigation checklists, test gates and system-by-system implementation guidance.

> **Scope and honesty:** This is an original technical synthesis, not a copy of external manuals, a verified disassembly, or a complete specification of proprietary RE2/RE3 engines. Distinguish hardware facts, published format descriptions, project-reported milestones, hypotheses, and features that require ROM-level verification. URLs are references for targeted follow-up, not proof that every linked resource has been inspected end-to-end. Do not claim a playable N64 ROM until built and boot-tested.

## 0. Fast start for Codex

1. Read this file, `RE3_N64_CODEX_MASTER_COMMANDS.md`, `PHASE_A.md`, and `docs/engineering/RE3_N64_C_Compilation_Codex_Handbook.md` if present.
2. Inventory all checked-out source files and archives; report actual paths, sizes, checksums and extraction status. Never assume a GitHub fork is installed software.
3. Compile and test the existing host-side C99 collision code first. Preserve passing tests.
4. Install or supply a pinned N64 toolchain and emulator; establish a minimal `.z64` boot smoke test on **4 MiB RDRAM, no Expansion Pak**.
5. Implement runtime subsystems in dependency order. Preserve all 169 RE3 RDT room records; confirm exact per-room semantics against source bytes.
6. Build asset converters that emit manifest entries with source hash, source offset, output hash, dimensions, format, endianness, decompression bound and validation status.
7. Record real measurements of peak RDRAM, ROM bank size, frame time, audio underruns and emulator results.
8. Convert FMV **last**, after a measured non-FMV ROM footprint.
9. `make game` must fail nonzero on missing required inputs or failing checks. Do not generate a placeholder ROM labeled complete.

### Source reliability tags

- **HARDWARE / PRIMARY:** hardware specifications, manuals, original developer postmortem.
- **TOOL AUTHOR:** upstream source repository and documentation; check version/branch.
- **RESEARCH:** reverse-engineering notes, wiki pages, format hypotheses; validate against actual binaries.
- **PROJECT-REPORTED:** milestone figures or files reported in our workspace; rerun validation.
- **PROPOSED:** an engineering design or behavior to implement; not an assertion about original RE2 N64 code.

## 1. Curated source directory — prioritize these URLs

### Historical RE2 N64 port and compression

- **Original developer account — Game Developer magazine, September 2000, Angel Studios FMV engineering:** https://ubm-twvideo01.s3.amazonaws.com/o1/vault/GD_Mag_Archives/GDM_September_2000.pdf — **PRIMARY**. The RE2 N64 article describes moving two PS1 CDs (~1.2 GB) to a 64 MB N64 cartridge, including roughly 15 minutes of FMV, with a movie budget of 25,165,824 bytes and ~165:1 ratio relative to raw frames. The cited raw-frame example uses 320×160, 24-bit, 30 fps. These are *historical RE2 figures*, not a ready-made codec or a guaranteed RE3 budget. Read the article itself before quoting detailed codec steps.
- **Secondary contextual summary:** https://hackaday.com/2026/02/03/how-resident-evil-2-for-the-n64-kept-its-fmv-cutscenes/ — **SECONDARY**; useful orientation, defer to original article for exact technical claims.

### PlayStation 1 hardware

- **PSX-SPX stable documentation:** https://psx-spx.consoledev.net/ — **HARDWARE / RESEARCH**. CPU, GPU, GTE, MDEC, SPU, CD-ROM, DMA, interrupts, controllers, memory cards, executable formats. Prefer stable over `/dev/` where AI-generated revisions may be unreviewed.
- **Original nocash PSX specs:** https://problemkaputt.de/psx-spx.htm — **HARDWARE / RESEARCH**.
- **PS1 emulator and debugging:** https://github.com/grumpycoders/pcsx-redux — **TOOL AUTHOR**.
- **PS1 homebrew toolchain:** https://github.com/Lameguy64/PSn00bSDK — **TOOL AUTHOR**.
- **PS1 file-format standards:** https://github.com/ps1dev/standards — **RESEARCH / TOOL AUTHOR**.
- **CD XA/STR extraction tool:** https://github.com/m35/jpsxdec — **TOOL AUTHOR**; confirm actual formats supported and CLI version before automation.

### Nintendo 64 hardware, toolchain and emulation

- **N64 Programming Manual index:** https://ultra64.ca/files/documentation/online-manuals/man/pro-man/pro03/contents.html — **HARDWARE**. Hardware, OS, RSP/RDP, DMA, memory, sprites, texture mapping, audio, controller interfaces and performance chapters. Historical proprietary SDK APIs do not automatically match libdragon.
- **N64 programming manuals catalogue:** https://ultra64.ca/resources/documentation/ — **HARDWARE**.
- **libdragon current docs:** https://libdragon.dev/ref/index.html — **TOOL AUTHOR**. GCC/Newlib, graphics, input, filesystem, audio and debugging. Pin the exact branch/tag used for the build.
- **libdragon upstream repository:** https://github.com/DragonMinded/libdragon — **TOOL AUTHOR**. Verify archive/migration status and select a maintained source before pinning.
- **libdragon alternative historic repository:** https://github.com/n64-tools/libdragon — **TOOL AUTHOR**, older implementation; don't mix build instructions with modern libdragon blindly.
- **ares emulator:** https://github.com/ares-emulator/ares — **TOOL AUTHOR**; use for actual 4 MiB emulation tests if installed.
- **mupen64plus:** https://github.com/mupen64plus/mupen64plus-core — **TOOL AUTHOR**; second-emulator regression testing.
- **N64 ROM/disassembly and symbol tooling:** https://github.com/ethteck/splat — **TOOL AUTHOR**; segmentation and ROM mapping require a verified configuration.
- **MIPS decompilation tooling:** https://github.com/Decompollaborate/modern-decomp — **TOOL AUTHOR**; consult license and compatibility.
- **N64 homebrew reference:** https://n64brew.dev/ — **COMMUNITY**; verify pages and versions.

### Resident Evil room / script / format research

- **REEVENGI tools repository:** https://github.com/pmandin/reevengi-tools — **RESEARCH / TOOL AUTHOR**.
- **RE3 `.RDT` notes:** https://github-wiki-see.page/m/pmandin/reevengi-tools/wiki/.RDT-%28Resident-Evil-3%29 — **RESEARCH**. Describes RE3 room data, SCA collision structures and init-script offsets; verify against the European disc and avoid assuming unknown fields.
- **Resident Evil modding community:** https://www.reshdp.com/re3/ — **COMMUNITY** (asset comparisons; not authoritative for binary structures).
- **Resident Evil Wiki:** https://residentevil.fandom.com/wiki/Resident_Evil_3:_Nemesis — **GAMEPLAY SECONDARY**. Use for cross-checking story/gameplay, not binary offsets.
- **The Cutting Room Floor:** https://tcrf.net/Resident_Evil_3:_Nemesis — **RESEARCH**; regional/unused content claims require binary verification.

### Our project resources

- **Main repository:** https://github.com/WackyWaldo90/RE3-N64-Port — source-of-truth for checked-in project code and reports.
- **Project master commands:** https://github.com/WackyWaldo90/RE3-N64-Port/blob/main/RE3_N64_CODEX_MASTER_COMMANDS.md — check branch/path.
- **Phase A report:** https://github.com/WackyWaldo90/RE3-N64-Port/blob/main/PHASE_A.md — snapshot, not live build verification.
- **User's ChatGPT desktop fork:** https://github.com/WackyWaldo90/ChatGPT — desktop UI reference, not N64 SDK or Codex itself.
- **Google Drive project folder:** https://drive.google.com/drive/folders/1uVm4YKG42ZFodwde0DCWLKXYzLVRr1W3 — access only when connector permissions allow.
- **Dropbox project subtree:** `/Source/resident evil 64&ps1` — inspect through the connected Dropbox tools; connector listings do not imply local byte access.

## 2. Console differences that dictate the port

| Concern | PS1 | Standard N64 | Conversion requirement |
|---|---|---|---|
| Main RAM | 2 MiB | 4 MiB RDRAM | Budget code, stacks, framebuffers, streamed backgrounds, geometry, audio and decompress buffers together. |
| CPU | MIPS R3000A family | MIPS VR4300 family | Recompile original-compatible logic in C; avoid raw PS1 executable reuse. |
| Graphics | PS1 GPU + GTE | N64 RSP + RDP | Rebuild rendering, materials, transforms, blending, masks and texture loading. |
| Media | CD sectors, XA/STR | Cartridge ROM, PI DMA | Repack into aligned ROM banks with streaming/decompression. |
| Video | MDEC-supported | No PS1 MDEC | Implement new software/RSP-assisted codec only if justified by profiling. |
| Audio | SPU + XA | N64 audio mixing/RSP options | Transcode samples/sequences and manage mixer buffers. |
| Controllers | PS1 digital/analog variants | N64 analog + A/B/Z/L/R/C | Explicit RE3 behavior mapping and input tests. |
| Save | PS1 memory card | Controller Pak / cartridge save design | Define storage backend, serialization, CRC and migration. |
| Region timing | PAL/NTSC variants | PAL/NTSC N64 variants | Avoid hardcoded frame-step; measure target timing and audio sync. |

**Memory target:** 4,194,304 total bytes, *not* 4 MiB for assets alone. Framebuffers, system structures, RSP/RDP buffers, stacks, heap and audio consume part of it. Use no Expansion Pak. The proposed four ROM banks are **logical cartridge asset groups**, not four physical RAM banks. A provisional 64 MiB ROM ceiling requires verification against hardware/flashcart/emulator deployment constraints; never infer it from 4 MiB RAM.

## 3. PS1 RE2/RE3 game systems and required N64 equivalents

Each entry below defines (A) observable game function, (B) what to extract or investigate, (C) N64 implementation and (D) acceptance test. The list is a *functional engineering inventory*, not a verified list of original proprietary function names.

### 3.1 Boot, main loop and state machine
- **Function:** initialize platform, start menu, update gameplay and dispatch scene transitions.
- **Inspect:** PS1 executable startup, game state dispatch, frame update order, interrupts.
- **Implement:** `n64_boot`, `game_state`, deterministic update loop, render/audio scheduling and watchdog logging.
- **Test:** reproducible boot into title; no crash or RAM overflow after 10 minutes of idle/menu transitions.

### 3.2 Title, options, difficulty and language
- **Function:** title screen, options, load/new game, difficulty settings, PAL localization.
- **Inspect:** UI assets, font glyphs, option flags, text encodings, regional behavior.
- **Implement:** scalable N64 sprite/UI renderer, language tables, settings persistence.
- **Test:** every menu route, input navigation and language string fits within screen bounds.

### 3.3 Room directory, stage IDs and loading
- **Function:** enter rooms, load cameras, masks, collision, scripts, objects and enemies.
- **Inspect:** `.RDT` headers, section pointers, room IDs, transitions, offsets and sector alignment.
- **Implement:** versioned `room_manifest`, ROM asset directory, decompression staging, deterministic room enter/exit.
- **Test:** iterate all expected rooms, validate pointers/bounds and render a diagnostic room viewer.

### 3.4 Fixed camera system
- **Function:** switch camera views as Jill/Leon/Claire crosses trigger regions.
- **Inspect:** camera coordinates, projection parameters, trigger polygons, transitions.
- **Implement:** fixed-view camera state, 3D projection, trigger evaluation, transition ordering.
- **Test:** camera cycling and in-world trigger crossings in representative rooms.

### 3.5 Pre-rendered backgrounds
- **Function:** display room backplates with characters rendered in front.
- **Inspect:** background images, source dimensions, palette/compression, regional variants.
- **Implement:** offline convert to supported N64 texture tiles/atlases, streamed DMA, cached decompression.
- **Test:** screenshot alignment, aspect ratio, palette accuracy, measured memory footprint.

### 3.6 Foreground masks and depth illusion
- **Function:** hide portions of character behind furniture, doorframes and scenery.
- **Inspect:** mask layers, polygons, priority/depth cues and camera associations.
- **Implement:** ordered overlay layers or depth masks supported by chosen renderer.
- **Test:** character crosses furniture boundaries without visible popping or ordering inversion.

### 3.7 Player locomotion and tank controls
- **Function:** walking, running, turning, backing up, quick-turn, aiming, firing, damage and death.
- **Inspect:** input mapping, acceleration, animation frames, state transitions and edge cases.
- **Implement:** explicit finite-state machine with fixed-timestep logic and animation event callbacks.
- **Test:** 180-degree turn, run/walk toggle, diagonal/analog handling, damage interruption.

### 3.8 RE3 dodge and action events
- **Function:** evasive maneuvers and context-sensitive reactions unique to RE3.
- **Inspect:** timing windows, animation branches, hitboxes, invulnerability behavior and triggers.
- **Implement:** documented timing parameters; test in controlled enemy encounter.
- **Test:** deterministic success/failure around each timing boundary.

### 3.9 3D geometry and materials
- **Function:** render character, weapon, enemy and interactive object meshes.
- **Inspect:** PS1 mesh indices, vertices, texture coordinates, texture pages, shading and draw order.
- **Implement:** N64-compatible vertex batches, material conversion, texture palettes and culling.
- **Test:** automated mesh count/vertex bounds; emulator screenshots with no missing triangles.

### 3.10 Skeletal animation and blending
- **Function:** idle/walk/run/aim/recoil/hit/death, enemy animation and cutscene posing.
- **Inspect:** joint hierarchies, rotation encodings, frame rates, animation event markers.
- **Implement:** offline conversion to compact joint/keyframe format; interpolation and event dispatch.
- **Test:** exact frame stepping, stable root motion, no bone explosions or NaN matrices.

### 3.11 Collision, navigation and stairs
- **Function:** block walls, slide against surfaces, transition stair elevation, detect doors and hazards.
- **Inspect:** RE3 RDT SCA records and shape flags; compare RE2 N64 runtime experimentally.
- **Implement:** validated collision loader, deterministic 2D movement/collision solver, height ramps, debug overlay.
- **Test:** walls, corners, stairs, narrow passages and no-clipping regressions.

### 3.12 Doors, room exits and loading transitions
- **Function:** trigger door interactions, fade/door animation, transfer state, unload/load assets.
- **Inspect:** door metadata, destination rooms, entry coordinates, scripts and door animations.
- **Implement:** transition state machine with error fallback for missing destination.
- **Test:** traverse complete representative loops without leaking memory.

### 3.13 Room scripts, triggers and events
- **Function:** puzzle switches, item spawns, cutscenes, enemy activation and conditional doors.
- **Inspect:** RE3 init/main script tables, opcode encoding, operand sizes, conditionals and event flags.
- **Implement:** bounded script VM/interpreter with opcode registry, unknown-opcode reporting and instruction limits.
- **Test:** synthetic opcode fixtures plus replay of verified in-game events; never silently ignore unknown opcodes.

### 3.14 Enemy AI and Nemesis pursuit
- **Function:** perception, movement, attacks, damage, state changes, pursuit and scripted encounters.
- **Inspect:** enemy spawn scripts, AI states, navigation limits, attack collision, animation event timing.
- **Implement:** per-enemy state machines and encounter director; Nemesis persistence only where verified.
- **Test:** repeatable encounters, room-boundary handling, no softlocks.

### 3.15 Combat, projectiles and hit detection
- **Function:** aiming, ammunition, hit selection, damage, knockback, weapon recoil and effects.
- **Inspect:** weapon stats, attack animations, enemy hit volumes, particle and sound triggers.
- **Implement:** collision query interface and data-driven weapon/enemy tables.
- **Test:** known test targets, ammunition counts, hit/miss boundaries and animation sync.

### 3.16 Inventory, item boxes and combination
- **Function:** inspect/use/combine/discard items, manage slots, item boxes and key items.
- **Inspect:** item IDs, descriptions, icons, capacity, combination rules and persistent flags.
- **Implement:** deterministic item database and inventory UI independent of renderer.
- **Test:** combinations, full inventory, key-item persistence, box transfers.

### 3.17 Puzzles, locks and progression
- **Function:** solve puzzles, consume key items, activate flags, open paths.
- **Inspect:** script conditions, puzzle states, room flags, item dependencies.
- **Implement:** serialized event flags with data-driven puzzle tables.
- **Test:** progression graph from start to ending; no impossible state or skipped mandatory flag.

### 3.18 Maps, navigation and status UI
- **Function:** room maps, player marker, health display, files and objectives.
- **Inspect:** map textures/geometry, localization, color/state conventions.
- **Implement:** atlas-backed 2D UI with live room/player state.
- **Test:** all maps load within UI memory budget and indicate current location.

### 3.19 Typewriters, save/load and game over
- **Function:** save at typewriter, consume ink ribbons as appropriate, restore full progression.
- **Inspect:** PS1 save serialization, slots, checksum, play time, difficulty and regional rules.
- **Implement:** new N64-native save schema with version, CRC, safe write and optional migration tools.
- **Test:** power-loss simulation, corrupted save rejection, reload reproduces game state.

### 3.20 Audio: BGM, ambient, SFX and voice
- **Function:** music changes, spatial/ambient sounds, footsteps, gunshots, speech and ducking.
- **Inspect:** PS1 SPU banks, sequences, XA tracks, event IDs, sample rates and loops.
- **Implement:** N64-supported mixer and compressed samples/sequence playback, streamed buffers.
- **Test:** no underruns during room transitions and combat; correct loop/end events.

### 3.21 FMV and in-engine cinematics
- **Function:** opening, narrative cutscenes, endings and voice/video sync.
- **Inspect:** PS1 STR/MDEC tracks, XA audio, cutscene triggers, lengths, subtitle localization.
- **Implement:** prototype codec after asset budget; consider low-resolution, chroma subsampling, frame pacing, audio sync, ROM streaming and optional RSP optimization.
- **Test:** measured CPU/RSP load, audio drift, peak RAM, full sequence playback.
- **Rule:** **FMV last**. Historical RE2 64 MB / ~25 MB FMV budget is a reference, not an RE3 allocation.

### 3.22 Mercenaries mode and unlockables
- **Function:** timed alternate mode, scoring, rewards, costumes and unlock flags.
- **Inspect:** alternate room/script references, timer/scoring, item shop or reward logic, completion flags.
- **Implement:** separate game-mode controller reusing rooms and gameplay engine.
- **Test:** entry/exit, timer, scoring, reward persistence and unlock regression.
- **Caution:** `R600.RDT` having zero SCA records does **not** by itself prove Mercenaries association. Verify room content, script references and actual behavior before assigning a role.

### 3.23 Costumes and boutique
- **Function:** unlock wardrobe, select costumes and swap character textures/models.
- **Inspect:** actual wardrobe room, key/item conditions, costume resource references.
- **Implement:** costume registry, persistence, compatible animation rig.
- **Test:** each outfit loads in gameplay and cutscenes; room identity must be verified.

### 3.24 Regional, timing and text compatibility
- **Function:** PAL display behavior, translated text, audio variants and save compatibility.
- **Inspect:** European RE3 disc ID and language resources, RE2 Europe N64 reference region, text encoding.
- **Implement:** explicit region metadata, timing abstraction and string table conversion.
- **Test:** PAL/NTSC emulator configurations, no clipping or desync.

### 3.25 Debugging and quality assurance
- **Function:** repeatable evidence for conversion correctness and game behavior.
- **Implement:** room viewer, collision overlay, animation inspector, asset manifest auditor, ROM map and memory profiler.
- **Test:** automated host unit tests + emulator smoke tests + screenshot/video capture with reproducible commands.

## 4. Known RE3 project data — verify rather than assume

The following are **PROJECT-REPORTED** historical milestones, not newly independently checked in this document:

- 169 RE3 `.RDT` room records; 168 reported collision-bearing rooms; 5,291 reported SCA collision records.
- `R600.RDT` reported 114,648 bytes with zero SCA collision records. Special-purpose status is an *open hypothesis*.
- M117–M120 include collision conversion/loader and C99 host tests. Custom `.r3sc` is a project format, **not proof of RE2 N64 native format**.
- M97 camera reconstruction was a prototype, not complete 169-room N64 background rendering.
- RE-Base v0.4 archive reportedly contains `RE3_N64_Engine_Collision.z64` (~30.8 MB) and source/media; a filename is **not** proof of a bootable game ROM.
- A split RE2 N64 reference ROM archive was prepared; Codex must locate all parts and verify hashes before disassembly.
- Previous Phase A report stated no installed N64 compiler/emulator and no verified bootable RE3 N64 ROM. Rerun environment audit to detect improvements.

## 5. Reverse-engineering protocol for RE2 N64 reference ROM

1. Confirm legal right to inspect the supplied game copy. Keep ROM, ripped assets and reconstructed images in private storage; publish scripts, metadata and original code rather than distributing commercial ROM contents.
2. Locate `Resident_Evil_2_N64_ROM.zip.part001` through `.part003` and `RE2_N64_ROM_parts_manifest.json`; do not assume root directory.
3. Reassemble in order, verify ZIP CRC, ROM size and SHA-256 against manifest; record every step.
4. Read N64 header; identify byte order (`.z64` big-endian, `.v64` byteswapped, `.n64` wordswapped) and normalize a **copy** only if required.
5. Build offset map of executable, candidate DMA tables, code, compressed resources, video, audio and free/unknown regions. Classify as confirmed/probable/unknown.
6. Use signatures only as hints; validate each asset format with parser bounds checks and cross-reference evidence.
7. Compare in-emulator behavior (camera change, stairs, door, inventory, save, FMV) against static findings.
8. Derive original-compatible, independently written RE3 implementation; avoid copying proprietary RE2 code/data into public project.
9. Publish `RE2_N64_ROM_ANALYSIS.md`, `RE2_N64_MEMORY_MAP.md`, `RE2_TO_RE3_CONVERSION_MATRIX.md`, `RE2_N64_ASSET_FORMATS.md` and test logs.

## 6. Asset converter contract

Every converter should accept a source file and explicit configuration and emit:

```json
{
  "source": "RDT/R100.RDT",
  "source_sha256": "<64-hex-hash>",
  "source_offset": 0,
  "source_size": 0,
  "asset_type": "room_collision",
  "format_version": 1,
  "output": "build/assets/rooms/R100.r3sc",
  "output_sha256": "<64-hex-hash>",
  "output_size": 0,
  "endianness": "big",
  "alignment": 16,
  "max_decoded_bytes": 0,
  "validation": "passed",
  "notes": "Replace placeholders with actual measured values"
}
```

Required converter checks: reject truncated headers, integer overflow, overlapping/escaping offsets, invalid dimensions, unsupported formats, unsafe filenames and inconsistent counts. Include reproducible fixtures and property tests. Asset extraction and ROM packing must never silently substitute dummy assets.

## 7. Four logical ROM banks (proposed)

- **Bank A:** boot/runtime code, menus, fonts, scripts and metadata.
- **Bank B:** rooms, camera tables, pre-rendered backgrounds, masks and maps.
- **Bank C:** character/enemy models, animations, collision, audio and gameplay effects.
- **Bank D:** FMV streams and associated audio, finalized last.

These are packaging categories, **not N64 physical banks**. All four compete for ROM capacity; only currently needed decoded assets should occupy RDRAM. The loader must validate offset, compressed size, decoded size, destination bounds, alignment, cache state and asset CRC/hash where practical.

## 8. Build, linker and memory validation

### Host baseline

```sh
cc --version
make --version
python3 --version
find . -maxdepth 4 -type f \( -name '*.c' -o -name '*.h' -o -name 'Makefile' -o -name '*.mk' \) | sort
# Compile/test actual existing targets, do not assume target names.
```

### N64 build pipeline (design, not an already working command sequence)

```text
make doctor        # verify pinned SDK, compiler, tools, emulator and asset sources
make test-host     # native C99 converter/logic unit tests
make assets        # reproducible conversion and manifest validation
make rom-smoke     # minimal .z64 boot test, 4 MiB hardware profile
make game          # full engine + assets + ROM packing; fail if incomplete
make verify-rom    # header, sizes, bank bounds, checksums and boot evidence
make report        # ROM map, memory profile, room coverage and emulator logs
```

Use libdragon's **actual pinned SDK build system and examples**; don't assume a generic `mips-linux-gnu-gcc` produces a valid N64 binary or that older `n64.mk` APIs match current libdragon. Compiler flags, startup objects, linker script, RSP microcode, ROM header/CIC and toolchain path must match the chosen SDK. The `.z64` extension alone is not a bootability test.

### Required acceptance outputs

- `reports/toolchain_versions.txt` and `reports/build.log`
- `reports/rom_map.csv` (bank, asset, offset, packed size, decoded max)
- `reports/room_coverage.csv` (all room IDs, background, camera, collision, scripts, status)
- `reports/memory.json` (measured peak, buffers, heap, stacks, framebuffer, audio)
- `reports/emulator_test.json` (emulator/version/config, test cases, exit status)
- Screenshots/videos of actual emulation when tooling supports capture
- ROM SHA-256 and boot-test result

**Fail gates:** missing assets, missing toolchain, unresolved required script opcode, ROM bank overlap, decoded size > allocation, measured peak > 4,194,304 bytes, failed emulator boot or missing mandatory room assets. For unresolved assets, record blocked state instead of claiming full-game completion.

## 9. Research questions requiring actual binary evidence

1. Which exact RE2 N64 ROM regions contain DMA tables, asset directories, models, backgrounds and FMV?
2. Which algorithms and microcode does this exact RE2 N64 regional revision use?
3. What are the real room-by-room RE3 European `.RDT` section counts and exceptions?
4. How are RE3 door destinations, cutscene triggers, enemy AI and Mercenaries states represented in source bytes?
5. What is the complete RE3 inventory/script opcode table and how are unknown opcodes handled?
6. What are the real peak N64 RAM and per-room streaming requirements on 4 MiB?
7. Which textures can be downsampled or palette-quantized without breaking masks and legibility?
8. What cartridge ROM size and flashcart/emulator configurations are actually supported by the target deployment?
9. Does RE-Base's `.z64` boot, and which parts of its code are compatible with our current workspace?
10. Which user-uploaded binary assets are accessible as actual bytes versus connector metadata only?

## 10. Recommended working order

**A. Provenance:** audit repository, split archives, SHA-256, tool versions, current milestone evidence.

**B. Platform:** compile minimal N64 libdragon ROM, boot in emulator at 4 MiB, capture proof.

**C. Rooms:** validate RDT parser, convert camera/background/masks/collision, run room viewer and transition tests.

**D. Gameplay:** input, Jill animations, doors, inventory, script VM, puzzles, enemies, Nemesis, save, Mercenaries and costumes.

**E. Polish:** audio, visual effects, region behavior, exhaustive progression QA.

**F. FMV last:** compress after measuring remaining ROM budget; validate A/V sync and memory.

**G. Release gate:** `make game` and emulator suite pass with reproducible hashes, no missing required rooms, measured <= 4 MiB peak RAM and clear remaining limitations.

## 11. Codex prompt to execute this handbook

> Read `RE2_RE3_PS1_TO_N64_CODEX_REFERENCE.md` and `RE3_N64_CODEX_MASTER_COMMANDS.md`. Treat this handbook as a curated offline reference and the linked sites as optional targeted verification, not as evidence of completed reverse engineering. First audit actual repo files, RE2 N64 split archives, RE-Base archives and installed tools. Preserve validated M120 collision work. Report a matrix of verified, inferred and blocked subsystems. Implement the smallest bootable 4 MiB N64 smoke ROM first, then progress room viewer -> gameplay systems -> FMV last. Never invent compiler/emulator output or claim a complete game before all acceptance tests pass. Commit only original source, conversion tools, docs, manifests and permissible metadata; keep commercial ROM/game asset bytes private.

## 12. Copyright, attribution and source-update policy

This file provides original summaries and links rather than reproducing external manuals or commercial game assets. A source URL can move or change; record retrieval date and version when Codex consults it. Consult original developer material before secondary writeups. Treat reverse-engineering community notes as hypotheses until validated on the exact regional binary. Keep copyrighted commercial ROMs and extracted game data out of a public GitHub repository unless you have redistribution rights. Never paste credentials, proprietary SDK packages or licensed binaries into build logs or commits.
