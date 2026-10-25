#!/usr/bin/env python3
"""RE3 N64: text-only, non-destructive toolchain source/build kit generator.
Run --install to create scripts and CI; run --check for environment diagnostics.
No proprietary SDK or ROM content. A compiler is built by CI, not embedded here.
"""
import argparse, pathlib, shutil, subprocess, sys
FILES = {
'Source/n64-toolchain/README.md': '''# Reproducible N64 compiler source/build kit

This is **source and recipes**, not a precompiled GCC distribution. The N64 GCC/binutils/newlib installation is too large for a single 25 MB GitHub upload. The authoritative toolchain sources live at https://github.com/DragonMinded/libdragon. Your fork `WackyWaldo90/libdragon` is a reference; verify upstream SHA and license before building.

## Fix for missing n64.mk
The inspected libdragon checkout has **`n64.mk` in the source repository root**. Do not assume `/opt/libdragon/n64.mk` or `include/n64.mk`. For a project Makefile, resolve `$(N64_INST)/n64.mk` if installed there; otherwise set `N64_MK` to the verified location in a source checkout. The compiler itself lives at `$(N64_INST)/bin/mips64-elf-gcc`, and SDK libraries normally live under `$(N64_INST)/mips64-elf/lib`. Do not confuse source checkout with installed SDK.

## Install in network-enabled Linux/GitHub Actions
Run `bash Source/n64-toolchain/build_from_source.sh`. It clones a **full SHA pinned** libdragon source, builds the compiler with upstream `tools/build-toolchain.sh`, installs the SDK with upstream Makefile, and saves evidence. Set `LIBDRAGON_COMMIT` to a reviewed **40-hex** commit before running. This can take considerable time and disk space. The script will not execute untrusted Dropbox toolkits or copy copyrighted ROMs.

GitHub Actions workflow `re3-n64-compiler.yml` runs only on manual dispatch, checks out repository and invokes the same build script. It stores metadata and logs, not toolchain binaries or commercial ROMs. A separate reusable compiler archive can be produced by an authorized build job and uploaded as a GitHub Actions artifact or release, not committed as a >25 MB source file. For reproducibility, pin container image digests and action SHAs before production use.

## Codex tasks
1. Read AGENTS.md and previous Phase A reports; do not overwrite conflicting source.
2. Audit upstream libdragon at exact commit. Verify `n64.mk` root location, `tools/build-toolchain.sh`, and `make install` targets.
3. Check Dropbox for `ares-source.tar.gz` and engineering guides, Drive for RE3 manuals, GitHub for libdragon fork and current scripts. These are reference resources; the actual compiler should come from the audited upstream source, not the proprietary Classic Toolkit.
4. Enable approved network access if blocked; never bypass sandbox restrictions. If the build cannot fetch dependencies, record URLs/errors and fail.
5. Run the source-build script in a clean Linux runner, record GCC version, target, installed `n64.mk` location and SDK libraries.
6. Fix `phase_a/Makefile` to use `N64_MK` discovered from actual installation, not hardcoded `/opt/libdragon/n64.mk`. Preserve standard upstream ROM rules.
7. Build a minimal original-content .z64, validate header, then run in a real emulator with 4 MiB; record screenshot and logs. Never mark emulator gate passed from compilation alone.
8. Create a **toolchain artifact** from the installed directory on a runner with sufficient artifact capacity; publish checksum and manifest. For public GitHub Source/ store only these source recipes, manifests and patches. If small-file upload is mandatory, use a deterministic chunk manifest and keep binary chunks in private storage or release artifacts; never claim they are source code.
''',
'Source/n64-toolchain/build_from_source.sh': '''#!/usr/bin/env bash
set -euo pipefail
: "${LIBDRAGON_COMMIT:?Set verified 40-character libdragon commit SHA}"
[[ "$LIBDRAGON_COMMIT" =~ ^[0-9a-fA-F]{40}$ ]] || { echo 'Full 40-char SHA required' >&2; exit 2; }
command -v git >/dev/null
command -v make >/dev/null
command -v gcc >/dev/null
command -v g++ >/dev/null
command -v wget >/dev/null
command -v tee >/dev/null
ROOT="${N64_WORK_ROOT:-$PWD/build/n64-toolchain}"
mkdir -p "$ROOT"
ROOT="$(cd "$ROOT" && pwd)"
export N64_INST="${N64_INST:-$ROOT/install}"
export BUILD_PATH="${BUILD_PATH:-$ROOT/build}"
export DOWNLOAD_PATH="${DOWNLOAD_PATH:-$ROOT/download}"
mkdir -p "$N64_INST" "$BUILD_PATH" "$DOWNLOAD_PATH" "$ROOT/evidence"
if [[ ! -d "$ROOT/libdragon/.git" ]]; then
  git clone https://github.com/DragonMinded/libdragon.git "$ROOT/libdragon"
fi
cd "$ROOT/libdragon"
git fetch origin "$LIBDRAGON_COMMIT"
git checkout --detach "$LIBDRAGON_COMMIT"
test "$(git rev-parse HEAD)" = "$LIBDRAGON_COMMIT"
test -f n64.mk
test -f tools/build-toolchain.sh
printf 'libdragon_commit=%s\\n' "$LIBDRAGON_COMMIT" | tee "$ROOT/evidence/source.txt"
# The upstream script downloads and builds binutils/GCC/newlib and may take substantial resources.
bash tools/build-toolchain.sh 2>&1 | tee "$ROOT/evidence/toolchain.log"
export PATH="$N64_INST/bin:$PATH"
"$N64_INST/bin/mips64-elf-gcc" --version | tee "$ROOT/evidence/gcc-version.txt"
"$N64_INST/bin/mips64-elf-gcc" -dumpmachine | tee "$ROOT/evidence/gcc-target.txt"
# SDK build/install uses the source-root n64.mk. Confirm install layout afterward.
make -j2 2>&1 | tee "$ROOT/evidence/sdk-build.log"
make install 2>&1 | tee "$ROOT/evidence/sdk-install.log"
find "$N64_INST" -name n64.mk -o -name libdragon.a | tee "$ROOT/evidence/installed-files.txt"
test -f "$N64_INST/mips64-elf/lib/libdragon.a"
if [[ -f "$N64_INST/n64.mk" ]]; then
  echo "$N64_INST/n64.mk" > "$ROOT/evidence/n64-mk-path.txt"
else
  echo "$ROOT/libdragon/n64.mk" > "$ROOT/evidence/n64-mk-path.txt"
fi
printf 'SDK installed: %s\\n' "$N64_INST"
''',
'.github/workflows/re3-n64-compiler.yml': '''name: RE3 N64 compiler source build
on:
  workflow_dispatch:
    inputs:
      libdragon_commit:
        description: 'Reviewed full 40-character libdragon commit SHA'
        required: true
        type: string
jobs:
  compiler:
    runs-on: ubuntu-24.04
    timeout-minutes: 360
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - name: Install host dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y --no-install-recommends build-essential git wget bzip2 ca-certificates libmpc-dev libmpfr-dev libgmp-dev texinfo flex bison python3
      - name: Build upstream compiler and SDK
        env:
          LIBDRAGON_COMMIT: ${{ inputs.libdragon_commit }}
        run: bash Source/n64-toolchain/build_from_source.sh
      - name: Upload build evidence
        if: always()
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        with:
          name: re3-n64-compiler-evidence
          path: build/n64-toolchain/evidence/
          if-no-files-found: warn
''',
'Source/n64-toolchain/diagnose.py': '''#!/usr/bin/env python3
import os, pathlib, shutil, subprocess, sys
root=pathlib.Path(os.environ.get('N64_INST','/opt/libdragon'))
print('N64_INST:',root)
for name in ('git','make','gcc','docker','mips64-elf-gcc'):
 print(name,shutil.which(name) or 'MISSING')
for p in (root/'n64.mk',root/'bin/mips64-elf-gcc',root/'mips64-elf/lib/libdragon.a',pathlib.Path('n64.mk'),pathlib.Path('include/n64.mk')):
 print(('FOUND' if p.is_file() else 'MISSING'),p)
print('NOTE: missing compiler/SDK is BLOCKED, not a passed N64 gate')
'''
}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true');ap.add_argument('--install',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
 if a.verify:
  print('PASS: embedded files',len(FILES));return 0
 if a.check:
  exec(compile(FILES['Source/n64-toolchain/diagnose.py'],'diagnose.py','exec'));return 0
 if a.install:
  for name,content in FILES.items():
   p=pathlib.Path(name)
   if p.exists() and p.read_text()!=content:
    print('CONFLICT, refusing to overwrite:',name,file=sys.stderr);return 2
  for name,content in FILES.items():
   p=pathlib.Path(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content);print('INSTALLED',name)
  return 0
 ap.error('choose --verify, --install or --check')
if __name__=='__main__':sys.exit(main())
