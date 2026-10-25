# RE3 N64 Port — Codex emulation, compilation, ROM testing and reverse-engineering instructions

**Repository:** https://github.com/WackyWaldo90/RE3-N64-Port  
**Scope:** Phases A–F; start with Phase A.  
**Status:** Instructions, not proof that an emulator or toolchain is installed in the Codex runtime.

## 1. Mission and non-negotiable rules

Establish a **reproducible, real N64 build-and-test loop** for an independently written RE3-inspired technical prototype. Do not claim that a ROM boots, that gameplay was observed, or that a test passed without executing it and saving evidence. Never use the commercial RE2 N64 ROM as bootcode, a base ROM, or a redistributed dependency; use RE2 N64 only as an engineering reference where authorized. Keep retail ROM/BIN/ISO, licensed audio/video, account credentials, and access tokens outside the Git repository.

If a task requires an unavailable dependency or blocked network access, stop retrying after a single documented diagnostic attempt. Report the precise command, error, and permission or package required. A Markdown file cannot enable cloud sandbox network access.

## 2. Available resource inventory (verify each at runtime)

| Resource | Location | Purpose | Access caveat |
|---|---|---|---|
| Project repository | https://github.com/WackyWaldo90/RE3-N64-Port | Code, CI, reports | Confirm writable checkout |
| Drive root | https://drive.google.com/drive/folders/1uVm4YKG42ZFodwde0DCWLKXYzLVRr1W3 | RE3, Emulators, Tools, Roms subfolders | Codex may not inherit ChatGPT Drive permissions |
| Drive RE3 milestones | https://drive.google.com/drive/folders/1_CJSbPlElT1ScldYqPJQGGi2ItQsBz9X | M93–M119, reference manual | Access via authorized connector or staged files |
| Dropbox project | `/Source/resident evil 64&ps1` | Engineering guides, PCSX-Redux, ares source, Pyrite64, RE3 PS1 files | Requires authorized Dropbox access |
| Prior starter package | `RE3_N64_Codex_Starter_FIXED.zip` in ChatGPT conversation | `src/main.c`, `Makefile`, `AGENTS.md`, M120 data | Must be explicitly staged into Codex workspace |
| N64 emulator | `ares-source.tar.gz` in Dropbox | N64 emulation, ROM tests | **Source archive**, not a confirmed installed executable |
| N64 engine/editor | `Pyrite64` in Dropbox, or `pyrite64-main.zip` if staged | libdragon/tiny3d example runtime | Optional; evaluate compatibility first |
| PS1 emulator | `pcsx-redux-main` in Dropbox | PS1 runtime investigation | Not N64 ROM emulator |
| Reverse engineering | `RE-Base-v0.4`, conversion guides, RDT/SCA milestone files | PS1 data analysis | Inspect actual formats before conclusions |

The Pyrite64 source README describes a libdragon/tiny3d-based engine/editor and recommends **ares v147+ or gopher64** for accurate emulation. This does not establish that any emulator is already installed in Codex.

## 3. Phase A0 — inspect workspace before downloading anything

Run and save the results in `reports/PHASE_A_ENVIRONMENT.md`:

```sh
pwd
find . -maxdepth 3 -type f | sort | head -200
uname -a
command -v gcc || true
command -v make || true
command -v cmake || true
command -v docker || true
command -v ares || true
command -v gopher64 || true
command -v mupen64plus || true
command -v libdragon || true
find /opt /usr/local /workspace -maxdepth 4 \( -iname '*ares*' -o -iname '*gopher64*' -o -iname '*libdragon*' \) 2>/dev/null | head -100
```

Do not assume that the current directory contains extracted ZIP contents. Inventory `milestones/M120`, `src/`, `tests/`, `tools/`, and `assets/converted/`. If only ZIPs exist, extract them safely and preserve provenance. Reject path traversal entries and archive bombs.

## 4. Phase A1 — establish N64 compilation

1. Prefer a pinned, documented **libdragon** toolchain for the minimal C starter. Consult the checked-in Makefile and the matching libdragon documentation before editing it. Avoid mixing incompatible libdragon releases and makefile templates.
2. If Pyrite64 is present, audit its dependencies and determine whether it is useful as an optional renderer or scene-management reference. **Do not replace the starter build with Pyrite64 without documenting the tradeoff.**
3. Install or use existing dependencies **only when the Codex environment permits it**. Prefer preinstalled tools or pinned container images; document checksums/versions. Do not commit toolchain binaries to the repository.
4. Implement a minimal N64 application that initializes video, displays a distinctive diagnostic screen with build ID, polls a controller, and loops safely. Use clean-room/open-source startup and linker support.
5. Produce `build/re3_phase_a.z64` via a reproducible command (e.g., `make rom`, after defining that target). Check the actual output, not just the Makefile exit code.
6. Verify ROM byte order, header, entry point, and file size with an independent inspector. **Header validity alone does not establish bootability.**

## 5. Phase A2 — emulator execution and evidence

1. Prefer a verified compatible **ares** build; if the supplied archive is source-only, check build prerequisites and compile it only if feasible. Alternative: gopher64 if available and compatible. Record exact emulator version.
2. Detect whether the Codex environment has a graphical display or headless-capable emulator invocation. Do not invent CLI flags: consult `--help` or source documentation.
3. Boot the newly built `.z64`. Capture stdout/stderr, exit status, emulator logs and, where possible, a real screenshot or framebuffer capture. If headless testing cannot confirm rendering, mark the result `UNVERIFIED DISPLAY`.
4. Confirm the diagnostic screen, controller handling (if input injection is supported), and sustained execution. Record duration and any warnings.
5. Store evidence under `reports/evidence/` and write `reports/PHASE_A_ROM_TEST.md` containing exact build command, emulator command, versions, observed behavior and blockers.
6. Never substitute PS1 emulator results for N64 ROM testing.

## 6. Phase A3 — automatic GitHub Actions pipeline

Add `.github/workflows/n64-ci.yml` only after choosing a pinned and working toolchain. CI should:

- Check out source and initialize required submodules.
- Run host C99/Python tests (including the M120 collision loader and bank validation where available).
- Build the minimal N64 ROM with the pinned toolchain.
- Run independent ROM structure checks.
- Run emulator smoke tests **only if** a reliable noninteractive execution path is verified; otherwise report a manual emulator gate instead of greenwashing.
- Upload `.z64`, build logs, test reports and evidence as GitHub Actions artifacts; do not commit generated ROMs to source control.
- Fail the workflow on compiler errors, failing tests, missing required assets or invalid ROM structure.

## 7. Reverse-engineering workstream (PS1 RE3 → independent N64 systems)

Use authorized source material and the user's engineering guides. Relevant Dropbox documents include `Resident_Evil_2_PS1_to_N64_Engineering_Guide.pdf`, `Resident_Evil_3_PS1_to_N64_Engineering_Guide.pdf`, and `RE2_N64_Port_Asset_and_Conversion_Reference.pdf`. **Read them and cite page numbers before attributing any specific technique to them.**

1. Inspect the RE3 Europe disc's executable and RDT/ARD structure with the existing extraction scripts. Preserve SHA-256 hashes and extraction provenance.
2. Analyze RE3 room scripts, camera tables, masks, background formats, geometry, collision and stair flags using M93–M120 reports. Existing converted collision banks are **custom project formats**, not proven native N64 formats.
3. For behavior investigation, use PCSX-Redux debugger and reproducible traces; record game revision and evidence. Do not guess opcode semantics from names alone.
4. Compare RE2 N64 storage, room transitions, camera behavior, background packing, audio and FMV techniques as a *reference*, separating observed facts from hypotheses.
5. For each conversion, create a host test: PS1 parse → intermediate representation → N64-friendly binary/texture → round-trip or bounds check. Track ROM/RAM budgets, alignment, endian order and checksums.
6. Keep a register with `VERIFIED`, `STATIC INFERENCE`, and `OPEN` labels; attach file paths, hashes, emulator screenshots/traces and guide page citations.

## 8. Phases B–F: gated implementation

- **B:** Two-room fixed-camera backgrounds and masking; demonstrate emulator rendering and bank loads.
- **C:** Jill placeholder/model, tank controls, animation state; verify input and frame stability.
- **D:** M120 collision loader integration, walls, floor, stairs, camera-aware collision debugging; regression tests.
- **E:** Door transitions and room streaming; repeat transitions without leaks or crashes.
- **F:** One enemy/combat prototype, HUD/inventory, audio, save prototype; measured performance and memory.

Do not proceed from A to B until a bootable ROM is observed. Do not claim completion of any phase without source, reproducible build, tests and emulator evidence.

## 9. Required reports and first Codex prompt

For each phase write `reports/PHASE_<LETTER>_REPORT.md` with: changed files, exact commands, compiler/emulator versions, ROM SHA-256, tests, screenshots/logs, ROM size, RAM estimates, blockers and next actions. Maintain `reports/REVERSE_ENGINEERING_EVIDENCE.md` and `docs/ASSET_PROVENANCE.md`.

**Paste into Codex:**

> Read `RE3_CODEX_N64_EMULATION_BUILD_TESTING.md` and `AGENTS.md`. Start with Phase A0 only. Inventory the repository, detect any staged ares/Pyrite64/libdragon resources, run existing host tests, and write `reports/PHASE_A_ENVIRONMENT.md`. Then proceed to a minimal libdragon ROM build and real emulator test if the required tools and permissions are available. Do not claim success without build logs and emulator evidence. Report missing resources and exact setup steps instead of endlessly retrying network access.
