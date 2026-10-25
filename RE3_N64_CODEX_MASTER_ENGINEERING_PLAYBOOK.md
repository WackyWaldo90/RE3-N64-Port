# RESIDENT EVIL 3 → NINTENDO 64
## Codex master engineering playbook: cross-compiler, SDK, emulator, reverse engineering, and PS1-to-N64 conversion

**Version:** 2026-10-25 | **Format:** UTF-8 Markdown (not a ZIP, ROM, executable, or installer)  
**Primary repository:** https://github.com/WackyWaldo90/RE3-N64-Port  
**Toolchain reference:** https://github.com/DragonMinded/libdragon  
**User's libdragon fork:** https://github.com/WackyWaldo90/libdragon  
**Candidate fork revision:** `e356bf3f56f7afbf7e5246329562f145965cfdfc` — confirm commit, compatibility and provenance before pinning.  
**Target:** Nintendo 64 VR4300, 4 MiB base RDRAM, no Expansion Pak, native big-endian `.z64`.  
**Current status:** Source-kit installers passed host checks; native compiler/SDK, ROM boot, and 4 MiB emulator verification have **not** been demonstrated. Phase A remains BLOCKED until real evidence exists.

> **How to use this document:** Place it in Google Drive. In Codex, attach the file or provide a link through a *connected, authorized* Google Drive tool that can read the document. Instruct Codex: **“Read this entire playbook as the execution plan. Inventory actual resources and permissions first, execute Phase A to real verification, and maintain evidence-backed gate reports. Do not stop at creating recipes.”** The file itself cannot grant Codex access to ChatGPT's separate Drive/Dropbox/GitHub connectors.

---

# 0. NON-NEGOTIABLE ENGINEERING RULES

You are Codex acting as lead Nintendo 64 C/C++ systems engineer, build engineer, and reverse-engineering integration lead for a clean, native RE3 N64 port. Execute code and tests; do not merely describe them. Build on the official libdragon-supported GCC/binutils/Newlib cross-toolchain, rather than inventing a new C compiler. Maintain clear separation between **observed original-game behaviour**, **reverse-engineered hypotheses**, **synthetic prototypes**, and **verified N64 runtime behaviour**.

1. Never claim Phase A passed without a working `mips64-elf-gcc`, installed libdragon, built `.z64`, real emulator boot, and verified 4 MiB mode. A command exiting zero while installing source recipes is not proof of a compiler.
2. Never fabricate emulator screenshots, logs, ROMs, source downloads, hashes, RAM peaks, or tests. Every report must link to real artifacts and command output.
3. Do not commit commercial RE2/RE3 ROMs, disc images, extracted copyrighted game assets, private Dropbox/Drive credentials, or proprietary SDK binaries to a public GitHub repository. Preserve private originals and work from authorized local copies.
4. Preserve existing work. Inventory files and Git status before edits; use branches and pull requests; reconcile collisions instead of blindly overwriting files. Do not execute untrusted Classic Toolkit binaries automatically.
5. Keep the 4 MiB N64 baseline as the mandatory target. 8 MiB is optional later, never a substitute for the 4 MiB pass.
6. Respect account, organization, network, CI, emulator and service access controls. When access is missing, request the narrow permission or a user-provided export; do not bypass controls.
7. Keep compiler/SDK dependencies pinned to immutable Git SHAs, container image digests where used, checksums, and build logs. Record host architecture and build configuration.
8. Prefer readable source files in GitHub; store large compiled toolchains as verified Actions artifacts/releases or approved Drive archives. The GitHub text connector cannot be relied upon to read arbitrary ZIPs as UTF-8.
9. Source `n64.mk` is at the **libdragon source root**; after `make install`, it is at **`$N64_INST/include/n64.mk`**. Do not use `$N64_INST/n64.mk` or invent `tools/libdragon` wrapper paths.
10. If external dependencies block work, make the most useful verifiable progress, record exact failed command and exit status, and state the smallest action that unblocks it. Never mark the blocked gate PASS.

# 1. ACCESS AND SOURCE-OF-TRUTH INVENTORY: GITHUB + DROPBOX + GOOGLE DRIVE

## 1.1 GitHub: working repository and fork catalog

Repository: `WackyWaldo90/RE3-N64-Port`. Read `AGENTS.md`, `PHASE_A.md`, `RE3_N64_Unblock_Kit.md`, `RE3_N64_C_Compilation_Codex_Handbook.md`, `RE3_CODEX_N64_EMULATION_BUILD_TESTING.md`, `RE3_N64_Workflow_Installer.py`, `RE3_N64_Codex_Source_Installer.py`, and every existing `.github/workflows/*.yml`. Check which actually exist. Inspect `Source/n64-toolchain/`, `phase_a/`, `reports/`, `codex_sources/`, source-kit manifests, and `Makefile`. Determine whether the newest installer files have actually been executed and committed; distinguish source kit staging from integrated game source.

Research forks (verify exact availability): `WackyWaldo90/libdragon`, `tiny3d`, `ares`, `mupen64plus-core`, `N64Recomp`, `ngine`, `biohazard-utils`, `Tool_Hazard`, `bio-tools`, `R3ditor-V2`, `re2studio`, `lib_bio`, `R3-Auto-Map-Gen`, `mkpsxiso`, `OG-Res-Bio-Evil-Workshop`. Forks are **references**, not automatically linked libraries, toolchain installations, or proven working converters. Verify license, branch, version, build instructions and compatibility before using.

Run locally in an authorized clone:

```bash
set -euo pipefail
git status --short
git rev-parse HEAD
git remote -v
find .github/workflows -maxdepth 1 -type f -print 2>/dev/null || true
find . -maxdepth 3 \( -name 'n64.mk' -o -name 'mips64-elf-gcc' -o -name '*.z64' \) -print
command -v docker || true
command -v mips64-elf-gcc || true
command -v ares || true
```

## 1.2 Dropbox: private originals and tools

Known user-owned references (existence reported in connected Dropbox; Codex must separately verify its own access):

- `/Source/resident evil 64&ps1/ares-source.tar.gz` — about 5.5 MB; **source archive**, not a runnable emulator.
- `/Source/resident evil 64&ps1/Resident Evil 3 - Nemesis (Europe).bin` and corresponding `.cue` — original PS1 disc image; private, do not commit.
- `/Source/resident evil 64&ps1/RE-Base-v0.4/RE3_N64_Engine_Collision.z64` — named reference; authenticity and contents must be verified; do not assume functional RE3 ROM.
- `Resident_Evil_3_PS1_to_N64_Engineering_Guide.pdf` and other conversion references.

If Codex has an authorized Dropbox integration, search by exact filename/path, inspect metadata, fetch only what is necessary and validate checksums. If Codex lacks it, request the user to export *specific* needed files to a private accessible workspace or configure an approved connection. Never print private download tokens in logs. Dropbox source archives may be useful for emulator builds but do not replace a functioning installed emulator.

## 1.3 Google Drive: manuals and milestone research

Known research: `RE3_Europe_PS1_Complete_Research_Reference_Manual.pdf` (Drive file ID `12iLC0i0tvkfjvo2ipS1pd1sE7fMxhCGI`), `RE2_N64_Port_Asset_and_Conversion_Reference.pdf`, `M10-M11.md` (bounded RDT/SCD inventory), and milestone M115–M119 (collision auditing, portability QA, collision binary pack, C loader and room collision manager). M119 previously identified as Drive file ID `1WSabgewe-GPLSrYBkKbOBBN1tWrq71sI`. Inspect actual revisions and evidence before treating milestones as production ready. Avoid assuming Drive file descriptions mean all raw RDT or collision data are present.

**Access matrix to create:** `reports/resources/access_matrix.csv` with columns `source,identifier,authorized,readable,downloadable,sha256,license_or_provenance,role,blocker,verified_at`. Keep private paths out of public logs when they reveal sensitive data. Use metadata only when contents are inaccessible. Do not silently substitute synthetic data for genuine RE3 assets.

## 1.4 Tool-access failure decision tree

- GitHub ZIP fails UTF-8 decode → request `encoding=base64` from supported GitHub contents API, or use `git clone` in a network-enabled runner, or read extracted UTF-8 source tree. Never interpret a binary as text.
- GitHub API 403 on writes → create a branch/PR through permitted credentials, or deliver a patch for user application; never claim committed.
- GitHub Actions lacks network → check documented environment permissions and allowlist; use approved caches/artifacts; never bypass policy.
- Google Drive/Dropbox connector not visible in Codex → request explicit connection/export. ChatGPT connectivity does not imply Codex connectivity.
- Archive inaccessible → record filename, hash/size if known, expected contents, alternate authorized path and impact; continue unrelated work.
- Large compiler >25 MB GitHub upload → do **not** split executable blindly into Git source. Build from pinned sources in CI; distribute as Actions artifact, Release asset, or Drive archive with SHA-256 and extraction instructions.
- Toolchain build exceeds CI time/disk → use BuildKit cache, dedicated toolchain workflow, or approved higher-capacity runner; report exact resource limit.
- Emulator requires GPU/Vulkan → use capable self-hosted runner or independently validated alternative; a headless emulator pass is not equivalent to Ares visual verification unless explicitly defined.

# 2. PHASE A: BUILD A REAL N64 GCC CROSS-TOOLCHAIN

## 2.1 Canonical toolchain source

Official libdragon: `https://github.com/DragonMinded/libdragon`; user's fork: `https://github.com/WackyWaldo90/libdragon`. Candidate fork commit `e356bf3f56f7afbf7e5246329562f145965cfdfc` was observed in the connected GitHub fork. Audit fork changes and licensing, and select an immutable commit. The libdragon fork contains root `Dockerfile`, root `n64.mk`, `tools/build-toolchain.sh`, and root `Makefile`. The `Makefile`'s install rule copies `n64.mk` into `$N64_INST/include/n64.mk`, libraries into `$N64_INST/mips64-elf/lib/`, and headers into `$N64_INST/mips64-elf/include/`. The upstream SDK uses `mips64-elf` target and VR4300/o64 flags; **do not override with incompatible PS1 or libultra ABI flags**.

**Prefer the actual pinned libdragon Dockerfile.** It builds the GCC/binutils toolchain in one stage and copies it to a runner image; it does not by itself establish that libdragon's SDK libraries and ROM tools are installed. Complete the SDK installation explicitly and verify it.

## 2.2 Reproducible Docker build commands (execute in network-enabled Linux runner)

```bash
set -euo pipefail
export LIBDRAGON_COMMIT=e356bf3f56f7afbf7e5246329562f145965cfdfc
mkdir -p build/toolchain
# Prefer audited official source; this fork URL is an authorized alternative.
git clone https://github.com/WackyWaldo90/libdragon.git build/toolchain/libdragon
cd build/toolchain/libdragon
git checkout --detach "$LIBDRAGON_COMMIT"
test "$(git rev-parse HEAD)" = "$LIBDRAGON_COMMIT"
test -f Dockerfile && test -f n64.mk && test -f tools/build-toolchain.sh
docker build --progress=plain --tag re3-n64-toolchain:${LIBDRAGON_COMMIT:0:12} . 2>&1 | tee ../docker-build.log
```

**Do not assume `docker build` installs SDK libraries.** Verify the built image and run the actual `make install` and `make -C tools install` in a container with the source mounted read-write. Container entrypoint, user permissions and installed tools must be inspected, not guessed. Example to adapt after checking the image:

```bash
# From inside build/toolchain/libdragon, after Docker image build:
IMAGE="re3-n64-toolchain:${LIBDRAGON_COMMIT:0:12}"
docker run --rm --entrypoint /bin/bash "$IMAGE" -lc \
  'echo "N64_INST=$N64_INST"; command -v mips64-elf-gcc; mips64-elf-gcc --version; mips64-elf-gcc -dumpmachine'

# Build and install SDK in a writable working copy inside the container.
# This creates a new derived image; ensure make and required host tools are available.
cat > Dockerfile.re3-sdk <<'DOCKER'
ARG BASE_TOOLCHAIN
FROM ${BASE_TOOLCHAIN}
COPY . /opt/libdragon-source
WORKDIR /opt/libdragon-source
RUN test -n "$N64_INST" && \
    make -j2 && \
    make install && \
    make -C tools -j2 && \
    make -C tools install && \
    test -f "$N64_INST/include/n64.mk" && \
    test -f "$N64_INST/mips64-elf/lib/libdragon.a" && \
    test -f "$N64_INST/mips64-elf/lib/libdragonsys.a" && \
    test -f "$N64_INST/mips64-elf/lib/n64.ld" && \
    test -x "$N64_INST/bin/n64tool"
DOCKER
docker build -f Dockerfile.re3-sdk --build-arg BASE_TOOLCHAIN="$IMAGE" \
  -t re3-n64-sdk:${LIBDRAGON_COMMIT:0:12} . 2>&1 | tee ../sdk-build.log
```

The Dockerfile above is a **candidate integration recipe**, not an already proven build. Fix exact Makefile targets and dependencies from pinned source. In particular inspect whether tools installation requires different targets, extra packages or `N64_INST` settings. Do not silently skip failed targets. Use an immutable digest for production image references and save `docker image inspect` metadata.

## 2.3 Toolchain acceptance test

```bash
set -euo pipefail
: "${N64_INST:?N64_INST must be set}"
for x in gcc g++ as ld objcopy objdump ar size; do
  test -x "$N64_INST/bin/mips64-elf-$x" || { echo "MISSING mips64-elf-$x"; exit 2; }
done
"$N64_INST/bin/mips64-elf-gcc" --version
"$N64_INST/bin/mips64-elf-gcc" -dumpmachine | grep -Fx mips64-elf
test -f "$N64_INST/include/n64.mk"
test -f "$N64_INST/mips64-elf/lib/libdragon.a"
test -f "$N64_INST/mips64-elf/lib/libdragonsys.a"
test -f "$N64_INST/mips64-elf/lib/n64.ld"
test -x "$N64_INST/bin/n64tool"
```

Also compile an isolated C file into a MIPS ELF object, inspect `readelf -h` and `objdump -f`, and verify big-endian MIPS target properties. Use the SDK's actual `N64_CFLAGS`, not arbitrary guessed ABI flags. Capture toolchain and SDK manifests in `reports/phase_a/toolchain.json` and `sdk.json`.

## 2.4 SDK Makefile rule for smoke project

`phase_a/Makefile` should follow this pattern, **adjusted against pinned libdragon examples**:

```make
N64_INST ?= /n64_toolchain
BUILD_DIR := build
SOURCE_DIR := .
N64_ROM_TITLE := RE3 N64 PHASE A
include $(N64_INST)/include/n64.mk

all: $(BUILD_DIR)/phase_a.z64

$(BUILD_DIR)/phase_a.elf: $(BUILD_DIR)/main.o

.PHONY: all clean
clean:
	rm -rf $(BUILD_DIR)
```

The libdragon `n64.mk` supplies object, ELF and Z64 pattern rules, but inspect whether its implicit linker rules and source-directory variables require additional prerequisites. Never hard-code `gcc` from the host or handcraft IPL3. If the pinned SDK's canonical sample differs, use the sample and document why.

## 2.5 C smoke program requirements

Create `phase_a/main.c` using the exact APIs supported by the pinned SDK. Start with libdragon's official console/video example. Initialize video output, show the text `RESIDENT EVIL 3 N64`, `PHASE A BOOT TEST`, `4 MiB BASE RAM`, and an incrementing frame counter. Poll input if supported; emit debug telemetry if supported. Use a conservative framebuffer such as 320×240 at 16-bit depth, accounting for all buffers. Implement an unmistakable visible change across frames, and keep running without relying on Expansion Pak. Do not fabricate successful output from code inspection. Compile, link, generate `.z64`, preserve ELF and map, and log commands and SHA-256.

## 2.6 ROM validation

Validate big-endian N64 header magic bytes `80 37 12 40`; ROM size, title, entry point, byte order, CIC-dependent checksums using a vetted N64-aware validator, and SHA-256. A header pass is **not** an emulator pass. Reject missing or empty ROM and mismatched hashes. Do not use the private RE2 reference ROM as an output ROM.

# 3. GITHUB ACTIONS: PERSISTENT COMPILER AND BUILD WORKFLOWS

Create real YAML files under `.github/workflows/` (Markdown-embedded YAML does not run):

1. `re3-toolchain-build.yml`: manual trigger and toolchain-source changes; checkout immutable libdragon SHA; Docker BuildKit build; SDK install; compiler acceptance test; archive installed prefix; generate SHA-256 and JSON manifest; upload compiler artifact. Prefer a Release asset or immutable OCI image for long-lived reuse because Actions artifacts expire.
2. `re3-phase-a-rom.yml`: use a verified pinned compiler artifact or image; rebuild if expired via approved fallback; compile minimal ROM; run ROM validator; upload ROM, ELF/map, build logs and checksums. **Do not rebuild GCC for every gameplay commit.**
3. `re3-phase-a-emulator.yml`: run actual emulator on supported runner, record version, command, screenshot/frame advancement and 4 MiB configuration. If no GPU/virtual-display support, use self-hosted or alternate supported emulator, explicitly labeled. Fail mandatory gate if no runtime evidence.
4. `re3-host-regressions.yml`: host-only tests for character, collision, RDT compiler and FMV prototypes; label as host tests, not native N64 verification.
5. `re3-phase-a-gate.yml`: download evidence from the **same source commit**, validate checksums, reject stale/missing artifacts and generate PASS/FAIL/BLOCKED reports. A missing emulator result must never be converted into PASS.

Pin third-party actions to immutable SHAs, give minimum `permissions: contents: read` by default, and explicitly grant any necessary upload/release permissions. Cache only trusted dependency builds. Keep network tokens and private Drive/Dropbox URLs out of logs. Upload original-content test ROM only; never upload commercial game data. Record runner architecture (e.g., Linux x86_64) and toolchain host compatibility.

## Compiler artifact design

Artifact `re3-n64-toolchain-<commit>-linux-x86_64.tar.zst` (or `.tar.gz`), containing installed N64 prefix, SDK headers/libs, compiler executables, manifest, checksums, and license notices. Measure compressed size. If >200 MB, do not claim it meets user's requested size: use an OCI image or release artifact and keep a small text-based reproducible rebuild recipe in GitHub/Drive. Validate extraction, executable bits, absolute prefix assumptions, shared library dependencies, and relocation. A compiler built for Linux x86_64 is not directly executable on Android or Windows; a Codex Linux runner can use it if compatible.

# 4. EMULATOR BOOT AND BASE 4 MiB VERIFICATION

Preferred: Ares (source may be in Dropbox; binary and graphics support must be verified). Alternate: Mupen64Plus or Gopher64 if independently tested for required features. Inspect actual CLI capabilities and display backends; do not invent flags. Record emulator binary hash/version, plugin/backend, N64 memory configuration, exact launch command, ROM hash, logs, screenshots and evidence that frame counter changed between frames. Emulator exit code alone is insufficient. For automated checks, use a real capture API or screen capture from the running emulator; never generate a fake screenshot from the expected text.

Memory evidence: show base 4 MiB selected, no Expansion Pak dependency, linker-map static allocation, framebuffer counts and dimensions, heap/stack high-water marks if instrumented, and peak memory if measurable. ROM file size is not RAM usage. `PHASE_A=PASS` only if A1 compiler, A2 SDK, A3 ROM build, A4 ROM integrity, A5 real emulator boot/frame advancement, A6 4 MiB configuration, and A7 representative target-side correctness tests all pass.

Target correctness suite: signed/unsigned 8/16/32/64-bit operations, integer division, floating point, struct layout and alignment, endianness, pointers, BSS/data initialization, stack, heap, controller/video and optional DMA. Compile with the N64 compiler and run target-side in emulator; host tests are supplementary.

# 5. RE3 GAME ENGINE: PS1 → N64 RESEARCH AND IMPLEMENTATION PLAN

**Do not activate gameplay builds until Phase A passes.** Meanwhile inventory and document conversion tools and input provenance. The PS1 game cannot be ported by mechanically recompiling MIPS R3000 instructions into N64 MIPS III. RE3 PS1 disc assets and game-specific formats must be parsed, validated, transformed, and consumed by a new or adapted native N64 runtime. N64 and PS1 have different graphics, audio, memory, timing and I/O architectures.

## 5.1 Original PS1 inventory and provenance

Authorized private RE3 Europe PS1 `.bin/.cue`: verify hashes and disc layout with suitable tooling; build a file table, sectors, sizes and per-file hashes. Previous research reported 169 `.ARD`, 169 `.BSS`, 27 `.PLD`, 84 `.PLW`, 24 `.TIM`, 4 `.PIX`, 13 `.STR`, 7 `.XAS`, 41 `.VB`, 34 `.VH`, 6 `.BGM`, and 546 `.DO1`–`.DO7` records (reported total 1,330 files); **treat counts as research to independently confirm**. Avoid extracting copyrighted content into public CI. Determine game build/region and differences before applying offsets.

## 5.2 RE3 RDT/ARD, SCD, camera, collision and rooms

Use R3ditor-V2, Tool_Hazard, biohazard-utils, lib_bio and user milestone sources as independent parsers/reference implementations. Validate formats with bounded offsets, sizes, endianness, pointer tables and explicit rejection of malformed records. A previous R3ditor inspection suggests a 96-byte RDT header of 24 little-endian dwords; the first count field is not a pointer. Candidate indices: 8 SCA collision; 9 RID camera; 10 RVD camera triggers; 11 LIT/PRI; 12 OBJ/TIM; 13 FLR floor; 14 BLK AI/pathfinding; 15 MSG; 16 RBJ animation; 18 SCD scripts. **These are hypotheses from one tool version, not a universal validated specification**. Cross-check against actual game rooms and another parser.

Prior Drive M10–M11 research reported 169 bounded RDT/SCD sections, 4,240 procedures, 125,179 instruction boundaries and 84 procedures containing opaque bytes. Preserve opaque regions; do not reinterpret unknown opcodes as valid logic. Record exact room IDs and provenance. Convert room camera data, floor/collision geometry, door triggers, background layers, item placements, scripts and actor spawns into a compact, versioned native intermediate representation with checksums. Retain original source offsets in debug manifests.

## 5.3 Collision and stairs

Integrate existing host-tested actor controller with actual M117–M119 collision loader/room manager, only after confirming their source and binary schemas. Verify room-to-room transitions, coordinate conventions, wall collision, swept/substep movement, floor-height sampling, staircase direction and scripted movement triggers. A synthetic stair interpolation pass does **not** prove correct original RE3 stair behaviour. Maintain tests for no wall tunnelling, 4 MiB room residency and door transitions.

## 5.4 Character models, animations, NPCs and enemies

Parse PLD/EMD-like data with validated skeleton, hierarchy, mesh and animation-bank mappings. Support shared actor framework for Jill, Carlos, Mikhail, Nicholai, campaign NPCs, zombies, enemies and bosses including Nemesis; each requires its own verified rig/animation/AI definitions. Do not assume all models share animation indices or collision dimensions. Implement per-character locomotion, turning, stairs, hit reactions and weapon/interaction states; compare with original PS1 gameplay capture when authorized.

## 5.5 Backgrounds, textures and RDP

Convert PS1 TIM/PIX/palettes and pre-rendered backgrounds to N64-compatible formats using libdragon conversion tools where applicable. Handle color depth, palette size, alpha/mask layers, screen composition, RDP TMEM limits, tiling and DMA. Preserve camera/background alignment and occlusion masks. Estimate memory, then measure on emulator. Use `rdpq` or other SDK-supported rendering methods as appropriate. Avoid assuming raw PS1 GPU commands are compatible with the N64 RDP.

## 5.6 Audio and FMV

Inventory PS1 XA/XAS/STR and VB/VH audio, BGM and sound triggers; validate sample rates, channels, looping and event timing. Prototype codecs separately from production streaming. Existing R3V1 FMV prototype is a portable C RLE decoder with a synthetic sample; it is **not** proof of actual RE3 FMV extraction, audio sync or N64 playback. For early boot-to-menu, prefer splash boards and main menu without opening FMV. Evaluate libdragon audio streaming and preview-branch movie features only after checking SDK compatibility, 4 MiB budget and measured performance.

## 5.7 AI, scripts, Mercenaries and saves

Reconstruct SCD control flow and room events conservatively, preserving unknown opcodes and original event ordering. Character/monster AI must reproduce state transitions, targeting, attack windows, navigation, spawns, boss-specific logic and event triggers. Mercenaries (Operation: Mad Jackal) needs its own timers, scoring, enemy waves, route logic, rewards and character-specific inventory/loadouts. Implement inventory, item box, typewriter/save data and save-media compatibility using supported N64 persistence methods; do not assume PS1 memory-card binary format is directly reusable.

## 5.8 RE2 N64 as an architectural reference, not a transplant

A private RE2 Europe N64 reference ROM was previously identified (64 MiB, header `80371240`, game code `NREP`). Use only for authorized local comparative analysis: asset compression, memory residency, camera/background organization, save systems, room loading, texture formats, audio and ROM banking. Do not copy its ROM code/assets into a public repository or assume the RE2 N64 engine already implements RE3 features. N64 ROM capacity and 4 MiB RDRAM are separate constraints.

# 6. RE3 N64 TARGET ARCHITECTURE AND MEMORY BUDGET

Proposed runtime modules (subject to measurement):

- `engine/platform/n64/`: libdragon startup, controller, video, audio, DMA, ROM filesystem, profiling, save backend.
- `engine/resources/`: archive index, decompression, streaming, resource cache, checksums.
- `engine/rooms/`: room loader, camera, collision, backgrounds, transitions, triggers.
- `engine/actors/`: actor registry, movement, skeleton, animations, combat, AI.
- `engine/scripts/`: validated SCD intermediate bytecode/interpreter.
- `engine/ui/`: splash, menu, inventory, map, saves, Mercenaries HUD.
- `tools/ps1_extract/`: private-input inventory and provenance, read-only parsers.
- `tools/convert/`: deterministic N64 asset transforms with manifests.
- `tests/host/` and `tests/n64/`: separate host/target tests.

**Memory ledger required:** code + BSS + stack + heap + one or more framebuffers + current/next room backgrounds + collision + active actor models/animations + audio streaming buffers + decompression scratch + UI. Start with explicit budgets, but only publish actual peaks after instrumentation. Use streaming/overlays, LRU caches, small decompression buffers, bounded allocations and fail-fast diagnostics. Do not promise all rooms or models resident simultaneously.

**Performance:** benchmark real emulator/hardware-compatible paths; evaluate `-O2`, `-Os`, and per-module alternatives, not universal `-O3`. Follow pinned libdragon defaults for `-march=vr4300 -mtune=vr4300 -mabi=o64` and associated link flags. Never mix PS1 MIPS R3000 binary code or incompatible Ultra64 o32 ABI objects with libdragon o64 binaries without proven bridges.

# 7. DELIVERY PHASES AND HARD GATES

- **Phase A — PLATFORM**: compiler + SDK + reproducible workflow + smoke ROM + ROM integrity + real emulator boot + 4 MiB mode + target correctness. Mandatory gate before gameplay.
- **Phase B — BOOT TO MENU**: splash boards, input, main menu, assets already converted, scene state, stable frame rate, 4 MiB test. No opening FMV required.
- **Phase C — ROOMS AND PLAYERS**: two actual RE3 rooms, backgrounds/cameras, door transitions, Jill/Carlos actor and animations, collision/stairs; screenshots and gameplay trace.
- **Phase D — SYSTEMS AND CAMPAIGN**: scripts, AI, items, audio, saves, enemies/bosses, Mercenaries, streaming and full content. Incremental verified slices, not one giant merge.

For each gate create a JSON report with `status`, `evidence_paths`, `commands`, `exit_codes`, `versions`, `sha256`, `limitations`, `next_action`, `git_commit`. Valid statuses: `PASS`, `FAIL`, `BLOCKED`, `INCOMPLETE`. A report generator must return nonzero if any mandatory gate is not PASS. Publish `reports/phase_a/summary.md` and keep source commit consistent across all artifacts. Do not automatically authorize the next phase on a host-only pass.

# 8. CONTINUOUS AUTONOMOUS EXECUTION LOOP FOR CODEX

At every iteration:

1. **Observe:** inspect repo HEAD, current Actions run, previous report, exact failing step and relevant connected-source availability.
2. **Hypothesize:** identify one specific root cause, alternatives and a minimal reproducible test.
3. **Repair:** implement a focused patch with tests, preserving existing project data.
4. **Verify:** rerun failing command, host tests, toolchain checks, ROM build, and emulator gate as applicable; capture raw logs.
5. **Record:** update manifests, checksums, status and rationale; open a PR/commit if authorized.
6. **Continue:** pick next highest-impact blocker. Avoid regenerating old scaffolds, declaring success from recipes, or repeating a known error without a new remedy.
7. **Escalate narrowly:** if blocked by account permission, network restriction, GPU, runner disk/time or missing private source, specify one exact user action and proceed with other independent tasks.

**Stop condition:** Phase A is PASS only with evidence for every mandatory gate. If no execution environment can build GCC or run the emulator, stop claiming completion, but deliver tested source/workflows and a precise blocked-gate report.

# 9. COPY-PASTE EXECUTION REQUEST FOR CODEX

> Read `RE3_N64_CODEX_MASTER_ENGINEERING_PLAYBOOK.md` fully. You are lead N64 compiler/SDK engineer and RE3 port integration lead. Start with an access matrix for GitHub, Dropbox and Google Drive; do not assume connections. Audit the current RE3-N64-Port repository and its workflow installer history. Build a **real pinned mips64-elf GCC/binutils/Newlib toolchain** from the audited libdragon Dockerfile in a network-enabled runner; install libdragon SDK and tools; verify the installed compiler executables and `$N64_INST/include/n64.mk`. Publish a checksum-verified reusable compiler artifact. Compile a minimal 4 MiB-compatible `.z64` using the SDK, validate ROM integrity, run it in a genuine emulator, capture visible frame advancement and prove base 4 MiB RDRAM configuration. Fix feasible errors and rerun until Phase A gates A1–A7 PASS or an external blocker is evidenced. Maintain immutable dependency pins, raw logs, ROM/compiler hashes, test reports and source commit. Never claim a recipe installer is a compiler, a valid ROM header is an emulator boot, or a host test is an N64 test. Do not start gameplay integration until Phase A passes. Separately prepare, but do not execute, the source-provenance-based PS1 RE3 RDT/SCD/collision/animation/background/audio conversion roadmap in this playbook. Commit reproducible text workflows and reports where authorized; keep commercial assets private.

# 10. REFERENCE CHECKLIST

Official source and SDK: https://github.com/DragonMinded/libdragon  
User fork: https://github.com/WackyWaldo90/libdragon  
Project: https://github.com/WackyWaldo90/RE3-N64-Port  
Ares: https://github.com/ares-emulator/ares  
Mupen64Plus: https://github.com/mupen64plus/mupen64plus-core  
Tiny3D: https://github.com/HailToDodongo/tiny3d  

**Final integrity principle:** This document is an executable engineering plan and technical knowledge map, **not a compiled compiler**. All claims of compilation, boot, performance and compatibility must come from actual future execution evidence.
