# RE3 N64 — Codex unblocking instructions

## Access
Codex cloud internet access is controlled by its environment configuration, not repository files. Enable internet access in the Codex environment settings, preferably with a dependency-domain allowlist. If using Codex CLI with workspace-write sandbox, set `[sandbox_workspace_write] network_access = true` in the appropriate Codex config where permitted. Never try to bypass organizational controls.

## Toolchain
Use upstream https://github.com/DragonMinded/libdragon and its official Docker wrapper. The workflow in `.github/workflows/n64-toolchain.yml` is a starting point and must be validated against the upstream wrapper path and supported commands. Pin the wrapper and container image by commit/digest once verified. Do not assume a local `gcc` is an N64 compiler.

## Emulator
Use https://github.com/ares-emulator/ares for actual N64 boot verification. Ares N64 requires Vulkan GPU support; ordinary GitHub-hosted runners may lack this. Run Ares on a GPU-enabled self-hosted runner or a capable local computer. Do not claim a ROM boot, screenshot, or peak RDRAM usage without evidence. Test alternative emulators separately if they are available, labeling accuracy limitations.

## Stage gates
A: cross-compiler executable found; libdragon sample ROM compiled; emulator boot recorded.
B: two rooms and camera backgrounds verified.
C: Jill input and animation verified.
D: collision/stairs verified.
Each stage must produce logs, artifact hashes and test results. Unfinished stages must remain marked BLOCKED or INCOMPLETE. Any mandatory stage that fails must return a nonzero process exit status.

## Source inventory
Dropbox: `/Source/resident evil 64&ps1/RE-Base-v0.4/RE3_N64_Engine_Collision.z64`, RE2/RE3 PS1-to-N64 engineering guides and RE2 N64 conversion reference. Drive: `RE3_Europe_PS1_Complete_Research_Reference_Manual.pdf`, `RE2_N64_Port_Asset_and_Conversion_Reference.pdf`. Library: `RE3_N64_ENGINE_RESEARCH.md`. Codex cannot read these merely because they are connected to ChatGPT; transfer authorized sources explicitly. Avoid committing commercial ROMs and copyrighted game assets to public GitHub.

## Runtime RAM
Target base N64 4 MiB RDRAM, no Expansion Pak dependency. Instrument code/heap/framebuffer/streaming/decompression peak usage; never substitute ROM file size for runtime RAM.

## GitHub Actions workflow (save separately as `.github/workflows/n64-toolchain.yml`)

The YAML below is embedded for reference; GitHub Actions will only execute it when saved as a separate workflow file. Verify upstream libdragon wrapper compatibility before relying on this starter.

```yaml
name: N64 toolchain verification
on:
  workflow_dispatch:
  push:
    paths:
      - '.github/workflows/n64-toolchain.yml'
      - 'Makefile'
      - 'src/**'
      - 'assets/**'
jobs:
  verify:
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - name: Check repository and network
        shell: bash
        run: |
          set -euo pipefail
          curl -fIL --retry 3 https://github.com/DragonMinded/libdragon
          test -f Makefile || { echo 'Missing Makefile'; exit 2; }
      - name: Install libdragon Docker wrapper
        shell: bash
        run: |
          set -euo pipefail
          curl -fsSL https://raw.githubusercontent.com/DragonMinded/libdragon/trunk/tools/libdragon -o /tmp/libdragon
          chmod +x /tmp/libdragon
          /tmp/libdragon --help
      - name: Compile ROM
        shell: bash
        run: |
          set -euo pipefail
          /tmp/libdragon make -j2
          find . -type f \( -name '*.z64' -o -name '*.n64' \) -print | tee /tmp/roms.txt
          test -s /tmp/roms.txt || { echo 'FAIL: no ROM produced'; exit 3; }
      - name: Upload ROMs
        uses: actions/upload-artifact@v4
        with:
          name: n64-rom-build
          path: |
            **/*.z64
            **/*.n64
          if-no-files-found: error
```
