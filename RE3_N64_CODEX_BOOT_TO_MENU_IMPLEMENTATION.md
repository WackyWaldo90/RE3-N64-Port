# RE3 N64 — Codex Boot-to-Main-Menu Implementation Contract

**Target:** WackyWaldo90/RE3-N64-Port · Nintendo 64 4 MiB RDRAM · no Expansion Pak required · C99 + pinned libdragon toolchain · no opening FMV.

## Critical correction to the Gemini specification

Do **not** implement a custom 4 KiB IPL3/`boot.s` or attempt to initialize the RDRAM controller from application code. IPL3 is a cartridge boot region with platform-specific startup behavior; it is not a drop-in generic MIPS program. The N64 boot ROM/PIF and SDK startup establish execution conditions before ordinary C code runs. Use libdragon's provided startup/linker/ROM packaging machinery. Do not overwrite the existing ROM header, CIC/IPL3, or patch the entry point without a validated boot-chain analysis. Do not mix proprietary Ultra64 SDK objects with libdragon without a proven compatible build.

The requested two-file design becomes:
- `src/platform/n64/init.c`: application-level platform initialization and teardown, with libdragon calls selected from the **pinned installed version**.
- `src/platform/n64/boot.s`: **optional** tiny application-owned assembly trampoline or debug helper, only if demonstrably necessary; **not** IPL3 or memory-controller initialization. Omit it entirely when unnecessary.

The actual startup is supplied by the SDK. Additional menu and asset modules are expected; do not force the entire game into two files.

## Preflight: inspect and preserve

1. Read `RE3_N64_CODEX_MASTER_COMMANDS.md`, `RE2_RE3_PS1_TO_N64_CODEX_REFERENCE.md`, `RE3_N64_BOOT_FIRST_CODEX.md`, `PHASE_A.md`, any current `Makefile.n64`, `.github/AGENTS.md`, and current source tree. Some documents may be absent: record this without failing unrelated tasks.
2. Locate `RE3_N64_Engine_Collision.z64` inside prior RE-Base archives if accessible. Preserve it unchanged. Record SHA-256, length, header, boot region, and checksum state. A valid header alone does not establish a working boot. Never write over this file.
3. Inventory **actual converted** RE3 splash/logo/main-menu assets; report file paths, hashes, format, resolution, palette, compression and license/provenance. Do not invent asset names, images, or conversion success. Determine whether these are already N64 runtime textures or only intermediate files.
4. Inventory current compiler, SDK, linker scripts, ROM packer, emulator, and CI environment. If network restricted, stop installation attempts and report a reproducible blocker; do not claim a successful build.
5. Preserve validated M120 collision host tests. Do not delete or rewrite working modules to accommodate the boot demo.

## Deliverable A — bootable ROM from source

Create a **separate** libdragon-based boot-to-menu ROM target (e.g. `make boot-menu`) with an independent output path such as `build/re3_boot_menu.z64`. `make game` should eventually depend on the validated target, but do not mislabel the boot-menu prototype as the full game.

Pin libdragon and its compatible toolchain to immutable revisions/releases (or image digests) with checksums. `N64_INST` must point to a real installation prefix containing the expected headers, libraries and `n64.mk` if used by the pinned SDK version. Never hardcode an assumed SDK path or claim it exists.

Use the **actual libdragon API of the pinned version**. At application startup, initialize debugging/console (optional), display/VI, controller input, timer, audio only if required for the menu, and filesystem/ROM asset access. Check API return values when supported. Keep initialization order consistent with libdragon examples. Prefer no AI/audio initialization if the splash/menu is silent.

Memory: target 4 MiB (4,194,304 bytes) including OS/SDK, framebuffers, stacks, heap, textures and code. Use a linker map plus runtime high-water tracking. Do not equate heap use with total peak RAM. Never write past detected physical RAM to probe its size. Detect expansion RAM only through documented SDK facilities or validated hardware/boot metadata, with safe fallback to **4 MiB**; **never require 8 MiB**. If exact detection is not supported by the chosen SDK, mark it unknown and enforce the 4 MiB budget.

Controller: initialize PIF/controller through libdragon, poll once per frame, debounce edges, map D-pad/analog vertical movement, A/Start select, B back. Controller Pak/Rumble Pak detection is **optional** for this milestone and must use documented accessory APIs only; do not issue speculative raw PIF commands. Absence of accessories must not prevent boot/menu.

## Deliverable B — splash boards then main menu

Use a small explicit state machine:

`BOOT_DIAGNOSTIC -> SPLASH_1 -> SPLASH_2 -> TITLE_MENU -> MENU_SELECTION -> (NEW_GAME_LOADING | OPTIONS | LOAD_GAME | MERCENARIES)`.

- Boot diagnostic: optionally display `RE3 N64 BOOT OK` and a running frame counter during debug builds; release builds can proceed directly to first splash.
- Splash screens: display **existing verified converted images** with correct pixel format and aspect ratio; allow A/Start to skip. Timings are configurable and frame-rate-independent; avoid a busy wait.
- Main menu: use converted RE3 menu/title images when verified, with a fallback text-only diagnostic menu clearly marked as a placeholder. Implement menu selection rendering and controller navigation. Do not claim exact original RE3 menu layout unless verified against the PS1 reference.
- Menu items: NEW GAME, LOAD GAME, OPTIONS, THE MERCENARIES **only where supported/appropriate**. Missing gameplay modules should show an explicit `NOT IMPLEMENTED` screen or diagnostics; do not silently hang or launch invalid pointers.
- No FMV player or opening movie. No fake 'game complete' banner.
- Keep menu state and input in separate testable C modules; no dynamic allocation inside the frame loop unless measured and justified.

Suggested layout (adapt to actual repository):
```
src/platform/n64/init.c
src/platform/n64/main.c
src/ui/boot_flow.c
src/ui/boot_flow.h
src/ui/main_menu.c
src/ui/main_menu.h
src/assets/menu_asset_index.c
include/re3_platform.h
scripts/verify_boot_menu.py
Makefile.n64
```
`src/platform/n64/boot.s` is **not required** unless a narrowly scoped assembly helper is justified and tested. Do not author a fake IPL3.

## Deliverable C — asset loading

Identify actual source assets and their conversion provenance. Create a deterministic asset index with names, offsets, lengths, alignment, pixel formats, expected checksums and target memory costs. Convert intermediate PNG/BMP/etc. to libdragon-supported texture/container formats using the pinned SDK's tools; do not assume any legacy `.bin` is already loadable. Keep original art unmodified. Validate boundaries, allocation size, alignment and load errors. Asset banks are **logical ROM groupings**, not physical RDRAM banks. Splash textures should be released or reused before allocating menu assets.

## Deliverable D — verification and acceptance

**Host gates**: `make test-host` succeeds with source-only checkout; existing M120 tests continue passing. State machine tests cover skip, timeout, menu wrap, debounced selection, no-controller and missing-asset cases.

**N64 gates**:
1. `make boot-menu` exits zero and creates a nonempty `.z64` with verified big-endian N64 header and appropriate ROM checksum via the pinned SDK's tooling.
2. Emulator boots the exact built ROM under **4 MiB** configuration. Record emulator name, version, command, exit status, logs and screenshots or video evidence.
3. First splash appears; second splash appears or is skipped; menu renders correctly; controller navigates; A/Start selects; B returns where applicable.
4. No crash/hang through at least 2 minutes of menu interaction; measure stack/heap and best available total peak RAM, clearly distinguishing estimates from measured totals.
5. Record ROM size, build commit, SHA-256, linker map, asset coverage and unresolved blockers. **Do not claim success if the emulator/compiler did not actually run.**

Save reports under `reports/boot_menu/`: `asset_inventory.csv`, `toolchain_versions.txt`, `build.log`, `rom_sha256.txt`, `memory_report.md`, `emulator_test.md`, and screenshots when produced. Keep compiled ROMs and commercial assets out of public GitHub by default; upload build instructions, metadata and original code.

## Required implementation order

1. Repository and asset audit, immutable baseline.
2. Toolchain and emulator preflight; fix broken CI independently.
3. SDK hello-world boot ROM (4 MiB) and emulator proof.
4. Display a plain diagnostic frame and read controller.
5. Integrate splash asset #1, then splash asset #2.
6. Render main-menu art and menu state machine.
7. Connect selections to explicit stubs/available game modules.
8. Run host and emulator tests; produce evidence and commit tested source.
9. Only after this milestone, load first room and Jill; defer FMVs until late ROM-budget phase.

## One prompt to execute

> Implement the boot-to-main-menu milestone specified in `RE3_N64_CODEX_BOOT_TO_MENU_IMPLEMENTATION.md`. Audit the repository and actual converted assets first. Use pinned libdragon startup rather than a custom IPL3. Preserve the original `RE3_N64_Engine_Collision.z64` and validated collision code. Produce a separate `make boot-menu` target, show existing splash boards then the RE3 title menu with working controller navigation, omit opening FMV, enforce 4 MiB RAM, run all available tests, and report exact evidence and blockers. Commit only tested source/config/report changes; never invent emulator or hardware results.

## Technical references

- libdragon: https://github.com/DragonMinded/libdragon
- libdragon examples and toolchain documentation: consult the exact pinned checkout
- ares emulator: https://github.com/ares-emulator/ares
- N64 hardware overview / programming: https://n64brew.dev/wiki/Main_Page
- PSX hardware reference (for asset conversion context): https://psx-spx.consoledev.net/

**Scope boundary:** This is an actionable implementation specification, not a compiled ROM or proof of a working menu. Actual file names and SDK calls must be verified against the checked-out project and installed version.
