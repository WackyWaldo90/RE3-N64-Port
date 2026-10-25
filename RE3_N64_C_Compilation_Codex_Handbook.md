# Resident Evil 3 — Nintendo 64 C Compilation Handbook

**Codex implementation reference | 2026-10-25 | Standard N64: 4 MiB RDRAM, no Expansion Pak**

## 0. Evidence and status (read before changing code)

This guide is tailored to the locally inspected `RE3_Codex_Workspace` and `RE3_N64_Base_Engine_Starter`. The existing workspace root `Makefile` delegates only to `milestones/M120` host tests; it **does not build a ROM**. M120's Makefile builds `r3sc_loader.c` and `r3sc_manager.c` with the host C compiler, then runs Python tests. The independent N64 starter has `src/main.c` and a libdragon-style Makefile, but N64 cross-compilation and emulator boot have **not** been verified. The connected repository Phase A report also states the N64 SDK, compiler, and emulator were unavailable. Do not equate a host GCC pass with N64 ROM success.

Known data: 169 RDT inventory entries, 168 rooms with 5,291 extracted collision records; `R600.RDT` has zero extracted SCA records and must be preserved. Its exact runtime function must not be assumed from SCA alone. R10F boutique should be included in the manifest after source verification.

## 1. Fixed hardware contract

- Target Nintendo 64 standard **4,194,304 bytes (4 MiB) RDRAM**, without Expansion Pak. Budget engine, stack, heap, display buffers, audio buffers, decompression scratch, current room and models *together*.
- N64 CPU is big-endian MIPS-family VR4300. Host machines are often little-endian; never cast on-disk structs directly to native pointers without byte-order and alignment checks.
- Cartridge ROM is not the same as RDRAM. Four proposed logical ROM banks are software packaging regions, **not** four hardware RAM banks.
- Treat **64 MiB ROM as a proposed upper target**, not a proven cartridge capacity. Verify cartridge mapper/ROM header/toolchain/emulator/flashcart behavior before enforcing the final limit. A 64 MiB image is 67,108,864 bytes; 64 Mbit is only 8 MiB. Never confuse units.
- The Expansion Pak must not be required for boot, rooms, audio, or gameplay.

## 2. Source layout and ownership

```text
AGENTS.md                         Codex policy, build gates, do-not-fake rules
Makefile                          one-command orchestration
config/target.json                RDRAM limit, validated ROM cap, codec choices
src/main.c                        N64 entry point
src/platform/                    boot, display, controller, ROM I/O, audio
src/engine/                      rooms, renderer, models, collision, gameplay
include/                         public C interfaces
assets/manifests/                all 169 RDTs, dependency and camera metadata
assets/converted/                generated deterministic assets (not source truth)
tools/                           extract, convert, validate, compress, pack
milestones/M120/                 existing collision source and host tests
build/                           generated ELF, ROM, map, reports
reports/                         acceptance evidence
```

Do not replace working M120 modules blindly. Keep original asset provenance and hashes. Do not publish proprietary RE2/RE3 ROMs or extracted copyrighted assets to a public repository without authorization; use private storage/artifacts or user-provided local paths.

## 3. Toolchain: install, pin, verify

Official libdragon source: https://github.com/DragonMinded/libdragon

The project needs: a compatible N64 MIPS cross-compiler and binutils, libdragon headers/libraries and build scripts, N64 ROM packer, GNU Make, Python 3, ares or Mupen64Plus emulator, and optional FFmpeg/image conversion tools. Prefer the SDK's documented setup or maintained container image; pin a commit or version in the build report. Do **not** assume a generic `mips-linux-gnu-gcc` produces an N64-compatible executable. Cross-compiler prefix and libdragon build variables depend on installed SDK version.

Preflight (shell; adapt paths to actual installation):

```sh
set -eu
command -v make
command -v python3
command -v gcc
: "${N64_INST:?Set N64_INST to your installed libdragon prefix}"
test -f "$N64_INST/include/n64.mk" || { echo 'Missing libdragon n64.mk'; exit 1; }
printf 'N64_INST=%s\n' "$N64_INST"
make --version | head -n 1
```

Check actual SDK `n64.mk` for exported `N64_CC`, `N64_CFLAGS`, `N64_LD`, `N64_LDFLAGS`, `N64_LIBS`, and `N64_TOOL`; **do not assume those symbols exist in every libdragon version**. If absent, migrate to the version's documented Makefile template instead of inventing commands. In a Codex sandbox, network permissions are controlled by the environment, not by repository configuration.

## 4. Two separate C compilation tracks

### A. Host compilation (fast and deterministic)

From current workspace:

```sh
make test
# or
make -C milestones/M120 test
```

Observed M120 compile recipe:

```sh
cc -std=c99 -O2 -Wall -Wextra -Werror \
  milestones/M120/r3sc_loader.c \
  milestones/M120/r3sc_manager.c \
  milestones/M120/test_r3sc_manager.c \
  -o /tmp/test_r3sc_manager
```

The test executable requires fixture paths. Prefer `make -C milestones/M120 test` so fixture paths resolve correctly. For new portable modules, add host unit tests and compile with `-std=c99 -Wall -Wextra -Werror -Wconversion` where practical; sanitize host-only tests with `-fsanitize=address,undefined -fno-omit-frame-pointer` when supported. Sanitizers are not N64 runtime tools.

### B. N64 cross-compilation (produces actual ROM)

The independent starter contains this **unverified SDK-version-specific** Makefile approach:

```make
ifeq ($(strip $(N64_INST)),)
$(error N64_INST is unset)
endif
include $(N64_INST)/include/n64.mk
BUILD_DIR := build
TARGET := $(BUILD_DIR)/re3_starter.z64
CFILES := src/main.c
OFILES := $(BUILD_DIR)/main.o
all: $(TARGET)
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)
$(BUILD_DIR)/main.o: src/main.c | $(BUILD_DIR)
	$(N64_CC) $(N64_CFLAGS) -c $< -o $@
$(BUILD_DIR)/re3_starter.elf: $(OFILES)
	$(N64_LD) $(N64_LDFLAGS) -o $@ $^ $(N64_LIBS)
$(TARGET): $(BUILD_DIR)/re3_starter.elf
	$(N64_TOOL) -l 2M -t "RE3 N64 STARTER" -o $@ $<
clean:
	rm -rf $(BUILD_DIR)
.PHONY: all clean
```

**Warning:** This snippet comes from the local starter; it is not a guarantee that current libdragon supports these flags or variables. `-l 2M` is a sample ROM image-size argument in that template, not a memory allocation and not our final cartridge limit. Verify with installed `n64tool --help`/SDK docs. Do not use the host `gcc` to build an N64 ROM.

Compilation stages: preprocess C → compile MIPS objects → link ELF with N64 linker script/runtime → inspect symbols/map → package N64 ROM header/image → validate byte order/header → boot in emulator. A valid `.z64` filename alone is not proof of a bootable ROM.

## 5. C language and ABI rules

- Use C99 for shared portable engine modules; keep hardware-specific code in `src/platform/`.
- Prefer `stdint.h` (`uint8_t`, `uint16_t`, `uint32_t`) and `stddef.h`. Use explicit width and checked offsets.
- Check arithmetic overflow before `offset + length`, `count * stride`, and buffer allocation.
- Explicitly read big-endian ROM fields (`read_be16`, `read_be32`) and little-endian PS1 source fields (`read_le16`, `read_le32`). Avoid packed-struct dereferencing and unaligned memory access.
- Document ownership/lifetime of asset pointers; ROM-mapped addresses, DMA buffers, cached/uncached aliases and CPU-visible pointers are not interchangeable.
- Handle N64 cache coherency for DMA using the installed SDK's documented primitives; avoid made-up platform APIs.
- Avoid unbounded recursion, VLAs of untrusted size, unbounded `sprintf`, undefined shifts, signed overflow and silent narrowing.
- Keep collision, room parsing and compression decoders fuzzable on the host.
- Keep code/data alignment required by the linker, DMA and texture formats; measure padding in ROM budgets.
- C and C++ may coexist, but agree on C ABI (`extern "C"` in C++ headers), initialization and exception/RTTI policy.

Example endian-safe parser:

```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
static bool read_be32(const uint8_t *p, size_t n, size_t off, uint32_t *out) {
    if (!p || !out || off > n || n - off < 4) return false;
    *out = ((uint32_t)p[off] << 24) | ((uint32_t)p[off+1] << 16)
         | ((uint32_t)p[off+2] << 8) | (uint32_t)p[off+3];
    return true;
}
```

## 6. Engine module interface and build dependencies

1. `n64_boot` initializes video, input, audio and a deterministic main loop; logs platform errors.
2. `memory_manager` owns 4 MiB RAM accounting, arena lifetimes, high-water marks and guard checks.
3. `rom_bank` validates asset index CRC, bounds, alignment and codec, and exposes `asset_open(id)`/`asset_close(id)` semantics.
4. `room_loader` resolves RDT ID, cameras, backgrounds, masks, SCA and script dependencies; transitions release previous-room memory.
5. `background_renderer` displays camera backgrounds and masks in correct order, with tested pixel formats and texture limits.
6. `model_renderer` streams character geometry/animation; uses RE3-specific animation data.
7. `collision` integrates the already-converted R3SC data with runtime movement; preserve all 5,291 records and report exceptions.
8. `controller` scans N64 input; maps analog/D-pad movement, A confirm, B cancel/run, Z aim, Start pause; implement quick-turn/dodge as RE3 rules. Bindings must be configurable.
9. `audio_engine` decodes/streams sound and music in bounded buffers; verify under room transitions.
10. `menu_system`, `save_system`, `gameplay`, `nemesis_ai`, `mercenaries` use the same asset/memory APIs. Validate save device support explicitly.
11. `fmv_player` is implemented and packed **last** after non-video ROM footprint is measured.

RE2 N64 is a behavioral and optimization reference, **not a verified source of C code**. Do not paste speculative original routines or claim exact RE2 symbols without disassembly evidence.

## 7. Four logical ROM banks and linker integration

Proposed bank definitions (changeable as evidence improves):

- Bank 0: engine executable, common UI, controller and system resources.
- Bank 1: room backgrounds, camera masks, camera metadata.
- Bank 2: models, animation, collision, sound, scripts and gameplay resources.
- Bank 3: FMV assets, built only after the rest of the game passes acceptance.

Each asset index entry must include stable ID, bank, offset, compressed length, decoded length, codec ID, alignment, checksum, and required RAM scratch. ROM offsets are not linker virtual addresses. Linker script determines code/data placement; asset packer determines ROM resource offsets. Validate that neither overlaps reserved ROM header/code regions.

Implement an asset pipeline: PS1 source verification → deterministic extraction → source format decode → N64 target conversion → compression → manifest/CRC → ROM bank pack → ROM linking/assembly → emulator verification. Cache conversions by source hash + converter version + target format + settings. If any required asset is missing, fail clearly; never substitute zero-filled fake content without an explicit diagnostic/demo mode.

## 8. RAM, video and sound budgets

For 320×240 16-bit framebuffers, one buffer occupies 153,600 bytes before alignment; two buffers 307,200 bytes, three 460,800 bytes. Z buffer, audio queues, textures and engine heaps are **additional**. Actual display allocation and SDK overhead must be measured. Avoid claiming the full 4 MiB is usable for game assets.

Use runtime high-water reporting for: static/BSS, stack, code/data, framebuffers, audio buffers, per-room background and mask buffers, model buffers, decompressor scratch and heap fragmentation. For every room/camera transition verify peak <= 4,194,304 bytes and retain safety margin. Also record ROM packed bytes, padding, code, assets, save resources and reserved FMV space.

Use appropriate lossless/lossy compression per asset and measure decode CPU/RAM cost. ROM size alone cannot decide codec selection. Video must be encoded for a validated cartridge budget and streaming throughput; FMV audio synchronization requires separate tests. Do not invent a RE2 proprietary codec implementation.

## 9. One-command `make game` contract

Codex should implement these real targets (the current workspace does not yet have them):

```make
.PHONY: game preflight host-test extract convert rom verify report
game: preflight host-test extract convert rom verify report
preflight:
	python3 tools/preflight.py
host-test:
	$(MAKE) -C milestones/M120 test
extract:
	python3 tools/extract_assets.py --manifest assets/manifests/sources.json
convert:
	python3 tools/convert_assets.py --manifest assets/manifests/rooms.json
rom:
	$(MAKE) -f Makefile.n64 all
verify:
	python3 tools/verify_rom.py build/re3.z64
report:
	python3 tools/build_report.py
```

**These `tools/*.py` scripts and `Makefile.n64` are proposed interfaces, not existing verified files.** Implement and test each before enabling `make game`. `verify` must include actual emulator execution and a captured boot/room test, not just header checks. Headless automation may require emulator-specific tooling and timeouts.

## 10. Test and acceptance matrix

| Gate | Required evidence | Failure behavior |
|---|---|---|
| Toolchain | SDK, compiler, linker, emulator versions | Stop before conversion |
| Host C | Unit tests, warnings, sanitizer run where possible | Stop |
| Data | 169 RDT manifest entries, 168 collision-bearing RDTs, 5,291 SCA records | Stop on mismatch, explain |
| Asset pack | offsets, checksums, codec roundtrip, size limits | Stop |
| N64 link | ELF and link map, correct ABI, no undefined symbols | Stop |
| ROM | valid header/endianness/size, no overlap | Stop |
| Boot | emulator log/screenshot, 4 MiB mode | Stop; no 'bootable' claim |
| Room viewer | camera/background/mask/collision test for every room including R600 special handling | Report incomplete coverage |
| Controller | real button and analog tests | Report unsupported bindings |
| Gameplay | doors, Jill, stairs, menus, enemies, Mercenaries, save | Report incomplete features |
| FMV | last-phase compression, playback/sync and remaining ROM budget | No final-complete claim |

Write machine-readable `build/reports/memory.json`, `rom_map.csv`, `room_coverage.csv`, `build_report.json`, test logs, and emulator screenshots. Record exact SHA-256 hashes and command lines. A ROM cannot be called complete until the game is actually playable end-to-end on standard 4 MiB hardware.

## 11. Immediate Codex execution plan

1. Inspect root `Makefile`, `milestones/M120/Makefile`, and starter `src/main.c`; preserve working host tests.
2. Install or locate a pinned libdragon toolchain and emulator; check the SDK's **current** sample build system.
3. Cross-compile a minimal boot/input `.z64`; verify with emulator and screenshots.
4. Add C modules for ROM bank, memory manager, room loader, renderer and controller incrementally, with host tests.
5. Integrate 169-room manifest, 168 collision-bearing files, R600 exception; do not silently discard R600.
6. Build all-room viewer, then models/audio/gameplay/menu/save; profile worst-case RAM.
7. Measure cartridge ROM usage, then add FMVs last.
8. Make `make game` orchestrate tested targets, with meaningful errors and reproducible outputs.

## 12. References

- libdragon: https://github.com/DragonMinded/libdragon
- ares emulator: https://ares-emu.net/
- Mupen64Plus core: https://github.com/mupen64plus/mupen64plus-core
- N64brew hardware/software reference: https://n64brew.dev/
- Project's current GitHub: https://github.com/WackyWaldo90/RE3-N64-Port
- Local project evidence inspected: `/mnt/data/RE3_Codex_Workspace/Makefile`, `/mnt/data/RE3_Codex_Workspace/milestones/M120/Makefile`, `/mnt/data/RE3_N64_Base_Engine_Starter/Makefile`, `/mnt/data/RE3_N64_Base_Engine_Starter/src/main.c`.

**Codex instruction:** Implement this as a verified, incremental pipeline. Never mark C modules, ROM generation, emulator boot, or complete-game conversion as done without artifacts and test evidence.
