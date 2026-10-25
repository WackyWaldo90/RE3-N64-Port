#!/usr/bin/env python3
"""Single UTF-8 GitHub-uploadable Phase A scaffold. No ROMs or SDK binaries included."""
import argparse
from pathlib import Path

FILES = {
'phase_a/Makefile': r'''N64_ROM_TITLE := RE3 N64 PHASE A
N64_ROM_REGION := E
BUILD_DIR := build
include $(N64_INST)/include/n64.mk

all: $(BUILD_DIR)/phase_a.z64

$(BUILD_DIR)/phase_a.z64: $(BUILD_DIR)/phase_a.elf
	$(N64_BINDIR)/n64tool -l 4M -t "$(N64_ROM_TITLE)" -h $(N64_ROM_REGION) -o $@ $<

$(BUILD_DIR)/phase_a.elf: $(BUILD_DIR)/main.o
	$(N64_CC) $(N64_LDFLAGS) -o $@ $^ $(N64_LIBS)

$(BUILD_DIR)/main.o: main.c
	@mkdir -p $(BUILD_DIR)
	$(N64_CC) $(N64_CFLAGS) -c -o $@ $<

clean:
	rm -rf $(BUILD_DIR)
.PHONY: all clean
''',
'phase_a/main.c': r'''#include <libdragon.h>
#include <stdint.h>

/* Deliberately no gameplay, assets, FMV, or Expansion Pak requirement. */
int main(void) {
    debug_init_isviewer();
    debugf("PHASE_A_START\\n");
    display_init(RESOLUTION_320x240, DEPTH_16_BPP, 2, GAMMA_NONE, FILTERS_DISABLED);
    while (1) {
        surface_t *fb = display_get();
        if (!fb) continue;
        graphics_fill_screen(fb, graphics_make_color(0, 0, 0, 255));
        graphics_set_color(graphics_make_color(255, 255, 255, 255), 0);
        graphics_draw_text(fb, 24, 40, "RE3 N64 - PHASE A");
        graphics_draw_text(fb, 24, 60, "4 MiB BASE HARDWARE TARGET");
        graphics_draw_text(fb, 24, 80, "BOOT / VIDEO SMOKE TEST");
        display_show(fb);
    }
}
''',
'phase_a/check_rom.py': r'''#!/usr/bin/env python3
import hashlib, pathlib, sys
p = pathlib.Path(sys.argv[1]); b = p.read_bytes()
assert len(b) >= 4096 and len(b) % 4 == 0, 'ROM length invalid'
assert b[:4] == bytes.fromhex('80371240'), 'not a big-endian z64 ROM'
assert any(b[0x1000:]), 'no nonzero payload after boot area'
print('ROM_HEADER_OK', p, 'bytes', len(b), 'sha256', hashlib.sha256(b).hexdigest())
print('NOTE: Header verification does not prove emulator boot or RAM consumption.')
''',
'.github/workflows/re3-phase-a.yml': r'''name: RE3 N64 Phase A - cross compiler and ROM
on:
  workflow_dispatch:
  push:
    paths:
      - 'phase_a/**'
      - '.github/workflows/re3-phase-a.yml'
jobs:
  build:
    runs-on: ubuntu-24.04
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
      - name: Check prerequisites
        shell: bash
        run: |
          set -euo pipefail
          command -v docker
          command -v git
          test -f phase_a/Makefile
          test -f phase_a/main.c
      - name: Fetch upstream libdragon and wrapper
        shell: bash
        run: |
          set -euo pipefail
          git clone --depth 1 https://github.com/DragonMinded/libdragon.git /tmp/libdragon-upstream
          git -C /tmp/libdragon-upstream rev-parse HEAD | tee libdragon-commit.txt
          test -f /tmp/libdragon-upstream/tools/libdragon
          cp /tmp/libdragon-upstream/tools/libdragon /tmp/libdragon-wrapper
          chmod +x /tmp/libdragon-wrapper
          /tmp/libdragon-wrapper --help
      - name: Cross-compile smoke ROM
        shell: bash
        run: |
          set -euo pipefail
          /tmp/libdragon-wrapper make -C phase_a -j2
          test -s phase_a/build/phase_a.z64
          python3 phase_a/check_rom.py phase_a/build/phase_a.z64 | tee phase-a-header-check.txt
      - name: Publish build evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: re3-phase-a-build-evidence
          path: |
            phase_a/build/phase_a.z64
            phase-a-header-check.txt
            libdragon-commit.txt
          if-no-files-found: warn
''',
'phase_a/EMULATOR_VERIFICATION.md': r'''# Phase A acceptance criteria (4 MiB N64)

1. Run GitHub Actions **RE3 N64 Phase A - cross compiler and ROM**.
2. If the build fails, preserve the full logs. Upstream libdragon wrapper or Makefile API changes must be fixed against the pinned commit printed in `libdragon-commit.txt`; do not claim a passing build.
3. Download the generated `phase_a.z64` from Actions artifacts (this file is original smoke-test code, not a commercial game ROM).
4. On a GPU-capable machine, open it in **ares** (preferred) with Expansion Pak disabled / 4 MiB memory configuration. Record emulator name, version, actual RDRAM setting, screenshot of three white text lines, and 30 seconds of stable display.
5. Repeat in Mupen64Plus or another independent emulator if available. Preserve emulator log and screenshot. A process exit code or valid ROM header alone is NOT a boot pass.
6. Confirm 4 MiB via emulator configuration plus memory instrumentation in the next iteration; the displayed text alone is not RAM measurement.
7. Only mark `BOOT_VERIFIED_4M` when both the real boot and actual 4 MiB configuration are evidenced. Until then status remains `UNVERIFIED`.

## Tool availability
- Dropbox: `ares-source.tar.gz` is emulator **source**, not a tested executable. Building ares typically requires graphics/Vulkan and platform dependencies.
- Drive: RE3 research manual is engine documentation, not an SDK or emulator.
- GitHub: forked libdragon/ares repositories are source references, not preinstalled binaries.
- Do not upload original RE2/RE3 commercial ROMs, SDK proprietary files or assets to the public repository.
- GitHub-hosted Actions runners generally cannot establish a GPU-backed ares graphical boot; do this on a GPU-enabled self-hosted runner or local computer.

## Security and reproducibility
- `actions/checkout@v4` and `actions/upload-artifact@v4` should be pinned to full audited action SHAs for production.
- Replace `git clone --depth 1` with a fixed reviewed libdragon commit after the first compatible build.
- The upstream wrapper is inspected/run from a third-party source; review before executing on privileged systems.
'''
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--install', action='store_true')
    ap.add_argument('--verify', action='store_true')
    args = ap.parse_args()
    if args.verify:
        for name, body in FILES.items():
            print(name, len(body.encode()), 'bytes')
        print('PASS: embedded UTF-8 sources available')
    if args.install:
        for name, body in FILES.items():
            p = Path(name)
            p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists() and p.read_text() != body:
                raise SystemExit('Refusing to overwrite changed file: '+name)
            p.write_text(body, encoding='utf-8')
            print('wrote', p)
    if not (args.install or args.verify):
        ap.print_help()

if __name__ == '__main__':
    main()
