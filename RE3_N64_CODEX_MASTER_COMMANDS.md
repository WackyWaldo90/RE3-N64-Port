# RE3 N64 Port — Codex Master Commands

**Revision:** 2026-10-25  
**Repository:** https://github.com/WackyWaldo90/RE3-N64-Port  
**Target:** Nintendo 64, standard **4 MiB RDRAM**, **no Expansion Pak**  
**Build goal:** `make game` produces and verifies a bootable RE3 N64 ROM **only after** all required implementation and verification gates pass.

> This document is a build specification and command playbook, **not evidence that a playable ROM already exists**. Do not invent build success, measured memory, decoded assets, or emulator screenshots. Preserve existing working code and data.

## 0. The master instruction for Codex

Copy the following as the **single task prompt** in Codex after adding this file to the repository:

```text
Read RE3_N64_CODEX_MASTER_COMMANDS.md, AGENTS.md (including .github/AGENTS.md), PHASE_A.md, docs/engineering/*, and the existing source/build scripts. Execute the phases in dependency order to implement a complete RE3 N64 port targeting 4 MiB RDRAM without Expansion Pak. First audit existing files and recover the toolchain; do not overwrite validated milestones. Build one-command `make game` orchestration with resumable stages and truthful acceptance gates. Preserve 169 RDT records, including R600 special scene and R10F boutique; convert every accessible environment and implement RE3 gameplay, sound, menus, controller and saves. Defer FMV conversion and final packing until all non-FMV systems are measured. Compile, boot and test the actual ROM in a 4 MiB N64 emulator; collect logs, screenshots, asset coverage and ROM/RAM reports. Commit incremental, testable changes. If an essential dependency is unavailable, stop that stage with precise evidence and actionable instructions; never fabricate completion.
```

**One-command entry point, once implemented:**

```bash
make game
```

**Important:** `make game` is a target Codex must implement. It is **not** assumed to work in the current checkout.

## 1. Hardware and capacity contract

| Property | Required behavior |
|---|---|
| RAM | Standard 4 MiB RDRAM (4,194,304 bytes), no Expansion Pak |
| Cartridge | Determine supported ROM ceiling from selected boot/flashcart/emulator/toolchain before committing budgets; **64 MiB is provisional** |
| CPU/ABI | MIPS-compatible N64 cross-compiler and toolchain; use SDK's supported ABI and flags |
| Graphics | N64 RSP/RDP through selected SDK; budget framebuffer, Z-buffer, textures and display lists |
| Controller | Original N64 controller; analog/D-pad tank controls and configurable actions |
| Assets | Four **logical ROM regions**, not four physical RAM banks |
| FMV | Convert and package last, using measured non-FMV size and RAM constraints |

Reserve runtime RAM for code/data, stack, heap, display buffers, audio buffers, DMA, current room, models, decompression scratch and worst-case transitions. Reject builds or test runs exceeding the budget. Measure rather than assuming all compressed assets can be decompressed simultaneously.

## 2. Mandatory repository audit (Phase A0)

```bash
pwd
find . -maxdepth 3 -type f | sort | head -250
git status --short
git log -5 --oneline
find . -iname '*R600*' -o -iname '*R10F*' -o -iname '*.RDT' | head -100
find . -iname '*Makefile*' -o -iname '*n64.mk' -o -iname '*AGENTS.md'
python3 --version
cc --version
make --version
command -v git
command -v 7z || true
command -v ffmpeg || true
command -v ares || true
command -v mupen64plus || true
command -v mips64-elf-gcc || true
```

Inspect all existing GitHub Actions YAML, toolchain scripts, asset manifests and M93–M120 milestone files. Record **present**, **missing**, **unreadable**, **untested** separately. If archives are on Dropbox/Drive only, connectors do not automatically make them accessible to a Codex shell: explicitly import authorized files and verify SHA-256 and archive integrity. Do not commit commercial PS1/N64 ROMs or copyrighted extracted assets into a public repository.

```bash
# After assets are actually copied into the workspace:
sha256sum path/to/archive.zip
python3 -m zipfile -t path/to/archive.zip
# Inspect before extraction; reject absolute paths, traversal, symlinks and archive bombs.
```

**Known evidence from previous project work:** inventory lists **169 RDT files**, **5,291 SCA records in 168 nonempty rooms**. `R600.RDT` has zero extracted SCA records and is a candidate Mercenaries presentation scene. Preserve it. `R10F` is associated with the Clothing Boutique. These associations require in-game verification before marking runtime behavior proven.

## 3. Toolchain setup (Phase A1)

Recommended independently developed N64 SDK: [libdragon](https://github.com/DragonMinded/libdragon). Follow the **current pinned libdragon documentation** for installation, toolchain prefix, ROM target, linker scripts and SDK Makefile integration; do not assume historical flags are compatible. Emulator: [ares](https://ares-emu.net/), with optional [Mupen64Plus](https://github.com/mupen64plus/mupen64plus-core). PS1 inspection: PCSX-Redux, jPSXdec; conversion: Python 3, Pillow, NumPy, FFmpeg, custom RE3 RDT/SCA parsers.

```bash
# Preflight commands; installation paths depend on the runner image.
command -v mips64-elf-gcc || true
command -v mips64-elf-ld || true
command -v mips64-elf-objcopy || true
printf 'N64_INST=%s\n' "${N64_INST:-UNSET}"
[ -n "${N64_INST:-}" ] && test -f "$N64_INST/include/n64.mk" && echo 'libdragon make integration found' || true
```

Prefer a **pinned container/devcontainer or reproducible CI image** containing the N64 SDK and emulator. GitHub Actions workflows belong in `.github/workflows/` (not the repository root). Managed Codex networking/sandbox permissions must be enabled by the environment owner; repository config files cannot bypass restrictions.

## 4. Required source layout (create only if absent)

```text
AGENTS.md
Makefile
src/
  main.c
  platform/n64_boot.c
  platform/controller.c
  platform/memory_manager.c
  platform/rom_bank.c
  graphics/background_renderer.c
  graphics/model_renderer.c
  game/room_loader.c
  game/collision.c
  game/doors.c
  game/game_state.c
  game/enemy_ai.c
  game/nemesis_ai.c
  game/inventory.c
  game/mercenaries.c
  game/menu_system.c
  game/save_system.c
  audio/audio_engine.c
  video/fmv_player.c
include/
tools/
  extract_ps1.py
  inventory_rdt.py
  convert_rooms.py
  convert_models.py
  convert_audio.py
  pack_banks.py
  audit_rom.py
  run_emulator_tests.py
tests/
assets/manifests/
assets/converted/     # generated; large/proprietary data ignored from public git
build/reports/
docs/engineering/
.github/workflows/
```

Preserve existing filenames when possible; this is a **target layout**, not permission to replace existing implementations. Ensure source dependencies are explicit in Makefiles.

## 5. C compilation rules (Phase A2)

Use C99 for portable host modules and the C standard/version supported by the selected N64 SDK for target code. Separate **host tests** from **N64 cross-compilation**.

```bash
# Host-only example: adapt paths to real files and test harness.
cc -std=c99 -O2 -Wall -Wextra -Werror -Iinclude \
  -c src/game/collision.c -o build/collision_host.o

# N64 target: compiler/linker/ROM invocation MUST come from pinned SDK examples.
# Do not treat host .o files as N64-compatible objects.
make doctor
make test
make rom
make emulator-test
make game
```

Suggested `Makefile` target contract:

| Target | Required purpose |
|---|---|
| `make doctor` | Check toolchain, emulator, SDK, input assets, disk and configuration |
| `make inventory` | Extract/validate room inventory and asset references |
| `make assets` | Incrementally convert non-FMV resources with hash-based cache |
| `make test` | Host unit tests, binary format roundtrips, asset audits |
| `make rom` | Cross-compile, link and pack a ROM with real SDK tools |
| `make emulator-test` | Boot ROM in 4 MiB configuration; capture logs/screenshots |
| `make budget` | Produce ROM map and peak RAM report, fail on overflow |
| `make fmv` | Final-phase video conversion only after non-FMV acceptance |
| `make game` | Orchestrate stages with prerequisites, stop on failures |
| `make clean` | Remove generated artifacts only; never source assets |

`make game` should invoke dependency targets and **fail nonzero** if required stages are unfinished. Do not create a placeholder `.z64` to satisfy a target. Keep build outputs out of Git unless intentionally distributing a lawful, independently built demo.

## 6. Four logical ROM banks (Phase B0)

- **Bank 0 — Engine:** compiled code, UI, runtime configuration and asset index.
- **Bank 1 — Rooms:** backgrounds, masks, cameras, room scripts and room metadata.
- **Bank 2 — Gameplay:** models, animation, collision, sound and gameplay tables.
- **Bank 3 — Video:** FMVs only; pack after other banks are final and measured.

For every packed resource, emit: `asset_id`, `kind`, `source_sha256`, `codec`, `rom_offset`, `compressed_bytes`, `decoded_bytes`, `alignment`, `crc32`, `estimated_peak_ram`, `room_dependencies`. Use deterministic ordering and endian-safe readers. Define a versioned format; never claim a custom container is a native RE2 N64 format. Track per-room streaming and simultaneous residency, not merely total bank size.

## 7. Room conversion and all-room viewer (Phase B1–B4)

1. Inventory every RDT by filename, size, offsets, cameras, backgrounds, masks, scripts, SCA records and dependencies.
2. Preserve all **169** entries. `R600.RDT` has no extracted collision records; do not treat as a universal blank loader or discard it. Preserve `R10F` Boutique.
3. Decode PS1 pre-rendered background images and foreground masks; convert to supported N64 texture/tile formats with measured quality and size.
4. Translate camera definitions and occlusion/masking; test depth ordering with character sprites/models.
5. Load one room at a time with camera selection, collision debug overlay, room-switch controls and optional diagnostic labels.
6. Record screenshot + room/camera ID for every tested environment. Track special/cutscene rooms separately from explorable rooms.
7. Validate room transitions and loading without exceeding 4 MiB peak RDRAM.

**Acceptance:** `build/reports/room_coverage.csv` lists all 169 RDTs and actual viewable-camera coverage. A file existing on disk is **not** proof it rendered on N64.

## 8. Models, collision and gameplay (Phase C–D)

- Convert PS1 model meshes, texture coordinates, animation skeletons and animations into versioned N64 runtime resources; preserve original animation timing.
- Implement Jill's tank controls, 180° quick turn, RE3 dodge, weapon aim, run/walk, hit reactions, stairs, doors, triggers and save rooms.
- Consume validated 5,291 SCA collision records (168 rooms), preserving geometry and flags. Add explicit special-case handling for R600 with no SCA.
- Implement enemies, Nemesis AI, encounters, event scripting, live selection, puzzles, inventory, ammunition mixing and Mercenaries gameplay from verified RE3 behavior.
- RE2 N64 is a **technical reference** for rendering and memory optimization, not permission to copy proprietary executable code.

## 9. N64 controller and menus (Phase C–D)

Proposed configurable default mapping (validate in playtests): analog/D-pad movement, `A` action/confirm, `B` run/cancel, `Z` aim, `Start` pause, `L/R` target cycling or alternative aiming, C-buttons for inventory/map/shortcuts. Implement dead zones, analog scaling, button-edge detection and controller disconnection handling. Quick turn and dodge must be distinct RE3 gameplay actions. Inventory, item examination, maps, save/load and Mercenaries screens need dedicated UI tests.

## 10. Sound, music and FMV (Phase D and final)

- Inventory PS1 audio/music, identify codecs and sample rates; convert to a supported runtime format and preserve looping/timing.
- Implement low-memory audio streaming/mixing with buffers counted against 4 MiB.
- FMV is the **last** major asset stage. After the non-FMV ROM is validated, compute remaining ROM space and a safety margin; select video resolution, frame rate, compression and audio quality based on measured cartridge/RAM budgets.
- Verify A/V sync and representative scenes on emulator. If FMVs do not fit, report quality/capacity trade-offs rather than silently dropping sequences.

## 11. Testing, reports and completion criteria

```bash
set -euo pipefail
make doctor
make inventory
make assets
make test
make rom
make emulator-test
make budget
# Only after the non-FMV game is functional and measured:
make fmv
make game
```

Required artifacts:

```text
build/game.z64                 # only when genuinely compiled
build/reports/toolchain.json
build/reports/asset_inventory.csv
build/reports/room_coverage.csv
build/reports/rom_map.csv
build/reports/memory.json
build/reports/test_results.json
build/reports/emulator_boot.log
build/reports/screenshots/
```

The CI pipeline should test host logic even if emulator availability is blocked, but **never label the ROM verified** without emulator execution. Track each phase as `not_started`, `blocked`, `in_progress`, `host_tested`, `rom_built`, `emulator_verified` or `hardware_verified` with evidence links.

## 12. Suggested GitHub Actions behavior

Create a workflow under `.github/workflows/re3-n64.yml` that checks out source, installs a **pinned** N64 toolchain/container, runs `make doctor`, `make test`, `make rom`, `make emulator-test`, `make budget`, and uploads logs/reports on failure as well as success. Use least-privilege permissions, avoid secrets in logs, and keep copyrighted input assets in approved private storage. If private game data is unavailable to CI, run a legal synthetic/test fixture and explicitly mark the full game build blocked.

## 13. Codex completion report format

At the end of each execution, Codex must report:

```text
COMMIT:
TOOLCHAIN:
INPUT ASSETS VERIFIED:
PHASES COMPLETED:
ROOMS RENDERED / TOTAL:
COLLISION RECORDS VERIFIED:
CONTROLLER TESTS:
ROM PATH / BYTES / SHA256:
ROM LIMIT / FREE SPACE:
PEAK RDRAM / 4194304:
EMULATOR / SETTINGS / RESULT:
SCREENSHOTS AND LOGS:
BLOCKERS:
NEXT ACTION:
```

## 14. Priority order

1. Fix SDK/compiler/emulator and build a real bootable 4 MiB-target ROM.
2. Render and verify all RE3 rooms/cameras, including Boutique and R600 special scene.
3. Integrate character models, movement, collision, stairs and door transitions.
4. Implement menus, audio, enemy AI, Nemesis, scripts, saves and Mercenaries.
5. Measure actual ROM and peak RAM; convert and pack FMVs last.
6. Run complete gameplay regression tests and produce the final verified ROM.

**Definition of done:** one command builds an independently implemented, playable RE3 N64 ROM, all required game content passes acceptance tests, and verified emulator memory use remains within 4 MiB without Expansion Pak. Until then, report measured progress and blockers accurately.
