#!/usr/bin/env python3
"""Install a pinned, source-built libdragon compiler CI workflow. UTF-8 only."""
import argparse
from pathlib import Path

WORKFLOW = r'''name: RE3 N64 - Build pinned compiler and smoke ROM
on:
  workflow_dispatch:
  push:
    paths:
      - '.github/workflows/re3-n64-source-toolchain.yml'
      - 'Source/n64-toolchain/**'
permissions:
  contents: read
jobs:
  compiler:
    runs-on: ubuntu-24.04
    timeout-minutes: 180
    env:
      LIBDRAGON_COMMIT: e356bf3f56f7afbf7e5246329562f145965cfdfc
    steps:
      - name: Checkout game project
        uses: actions/checkout@v4
      - name: Checkout exact libdragon source
        shell: bash
        run: |
          set -euo pipefail
          git init /tmp/libdragon
          git -C /tmp/libdragon remote add origin https://github.com/DragonMinded/libdragon.git
          git -C /tmp/libdragon fetch --depth 1 origin "$LIBDRAGON_COMMIT"
          git -C /tmp/libdragon checkout --detach FETCH_HEAD
          test "$(git -C /tmp/libdragon rev-parse HEAD)" = "$LIBDRAGON_COMMIT"
          test -f /tmp/libdragon/n64.mk
          test -f /tmp/libdragon/tools/build-toolchain.sh
          test -f /tmp/libdragon/Dockerfile
      - name: Build pinned toolchain container from audited source
        shell: bash
        run: |
          set -euo pipefail
          docker build --progress=plain -t re3-n64-toolchain:"$LIBDRAGON_COMMIT" /tmp/libdragon
      - name: Build and install SDK into compiler image
        shell: bash
        run: |
          set -euo pipefail
          cat > /tmp/libdragon/Dockerfile.re3 <<'EOF'
          FROM re3-n64-toolchain:e356bf3f56f7afbf7e5246329562f145965cfdfc
          COPY . /src/libdragon
          WORKDIR /src/libdragon
          RUN make -j2 && make tools -j2 && make install && make tools-install
          RUN test -f "$N64_INST/include/n64.mk" && test -f "$N64_INST/mips64-elf/lib/libdragon.a" && command -v mips64-elf-gcc
          EOF
          docker build --progress=plain -f /tmp/libdragon/Dockerfile.re3 -t re3-n64-sdk:"$LIBDRAGON_COMMIT" /tmp/libdragon
      - name: Compile minimal 4 MiB ROM and record evidence
        shell: bash
        run: |
          set -euo pipefail
          mkdir -p build/phase_a
          docker run --rm -v "$PWD:/work" -w /work re3-n64-sdk:"$LIBDRAGON_COMMIT" bash -euc '
            mips64-elf-gcc --version | head -1 | tee build/phase_a/compiler-version.txt
            test -f "$N64_INST/include/n64.mk"
            test -f "$N64_INST/mips64-elf/lib/libdragon.a"
            make -C Source/n64-toolchain/smoke clean all
          '
          python3 Source/n64-toolchain/check_rom.py build/phase_a/re3_phase_a.z64 | tee build/phase_a/rom-check.txt
          sha256sum build/phase_a/re3_phase_a.z64 | tee build/phase_a/rom-sha256.txt
          printf 'libdragon=%s\n' "$LIBDRAGON_COMMIT" > build/phase_a/manifest.txt
          printf 'EMULATOR_BOOT=BLOCKED (requires actual emulator run)\n4MIB_RUNTIME=BLOCKED (requires base-RDRAM emulator evidence)\n' > build/phase_a/runtime-gates.txt
      - name: Export reusable compiler and SDK archive
        shell: bash
        run: |
          set -euo pipefail
          docker create --name re3-toolchain-export re3-n64-sdk:"$LIBDRAGON_COMMIT" >/dev/null
          docker cp re3-toolchain-export:/n64_toolchain build/phase_a/n64_toolchain
          docker rm re3-toolchain-export
          tar -C build/phase_a -czf build/phase_a/re3-n64-toolchain.tar.gz n64_toolchain
          rm -rf build/phase_a/n64_toolchain
          sha256sum build/phase_a/re3-n64-toolchain.tar.gz > build/phase_a/toolchain-sha256.txt
      - name: Upload compiler, smoke ROM and evidence
        uses: actions/upload-artifact@v4
        with:
          name: re3-n64-compiler-and-smoke-rom
          path: build/phase_a/
          if-no-files-found: error
          retention-days: 14
'''

MAKEFILE = r'''N64_INST ?= /n64_toolchain
BUILD_DIR := ../../../build/phase_a
SOURCE_DIR := .
N64_ROM_TITLE := RE3 PHASE A
include $(N64_INST)/include/n64.mk

.PHONY: all clean
all: $(BUILD_DIR)/re3_phase_a.z64
$(BUILD_DIR)/re3_phase_a.z64: $(BUILD_DIR)/main.o
$(BUILD_DIR)/main.o: main.c
	@mkdir -p $(BUILD_DIR)
	$(N64_CC) $(N64_CFLAGS) -c -o $@ $<
clean:
	rm -f $(BUILD_DIR)/main.o $(BUILD_DIR)/re3_phase_a.elf $(BUILD_DIR)/re3_phase_a.z64
'''

MAIN = r'''#include <libdragon.h>
#include <stdio.h>
int main(void) {
    console_init();
    console_set_render_mode(RENDER_MANUAL);
    while (1) {
        console_clear();
        printf("RE3 N64\nPHASE A BOOT TEST\n4 MiB BASE RAM\n");
        console_render();
        wait_ms(100);
    }
    return 0;
}
'''

CHECK = r'''#!/usr/bin/env python3
import hashlib, pathlib, sys
p = pathlib.Path(sys.argv[1]); data = p.read_bytes()
assert len(data) >= 4096, 'ROM too small'
assert data[:4] == bytes.fromhex('80371240'), 'Not big-endian .z64'
print('ROM_HEADER=PASS bytes=%d sha256=%s' % (len(data), hashlib.sha256(data).hexdigest()))
'''

FILES = {
    '.github/workflows/re3-n64-source-toolchain.yml': WORKFLOW,
    'Source/n64-toolchain/smoke/Makefile': MAKEFILE,
    'Source/n64-toolchain/smoke/main.c': MAIN,
    'Source/n64-toolchain/check_rom.py': CHECK,
}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--verify',action='store_true')
    parser.add_argument('--install',action='store_true')
    parser.add_argument('--root',default='.')
    args=parser.parse_args()
    assert args.verify or args.install
    for name, content in FILES.items():
        assert content and '\x00' not in content
        if args.install:
            target=Path(args.root)/name
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists() and target.read_text()!=content:
                raise SystemExit(f'Conflict: {target}; inspect manually, no overwrite performed')
            target.write_text(content)
        print(('INSTALLED ' if args.install else 'VERIFIED ')+name)
if __name__=='__main__': main()
