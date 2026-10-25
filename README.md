# RE3 N64 — Toolchain transfer kit

This kit **does not contain** a compiler, libdragon SDK or emulator. It safely transfers a **user-provided, complete, licensed and verified** toolchain archive in pieces of at most 24 MiB (25,165,824 bytes), below a 25 MB decimal limit. No parts are generated until the real archive is supplied.

## Preferred toolchain

- libdragon SDK and its documented compatible toolchain: https://github.com/DragonMinded/libdragon
- libdragon build instructions: https://github.com/DragonMinded/libdragon/wiki
- Ares emulator: https://github.com/ares-emulator/ares

Use the upstream supported installation method, including a pinned commit/release and checksums. Avoid bundling an arbitrary `mips64-linux-gnu-gcc` as a substitute for a supported N64 bare-metal toolchain. A Docker image or native toolchain may be used depending on the Codex execution environment. An SDK checkout alone is not a compiler distribution.

## Pack (on a machine with the real archive)

```bash
python3 split_toolchain.py /path/to/verified-n64-toolchain.tar.xz --output n64-toolchain-parts
```

Upload `manifest.json` and all `.partNNN` files to a **private** repository or artifact store if licensing permits. Prefer GitHub Releases or an external artifact store over committing hundreds of megabytes of binaries into Git history. Public hosting requires checking license and redistribution terms for every included component.

## Reconstruct (inside Codex)

```bash
python3 reconstruct_toolchain.py n64-toolchain-parts --output /tmp/n64-toolchain.tar.xz
sha256sum /tmp/n64-toolchain.tar.xz
```

The `--output` filename must match the actual archive format; no extraction happens automatically. After checksum verification, inspect archive members and extract using the correct format. Do not execute arbitrary scripts from an unverified archive.

## Configure and verify

Install the toolchain according to its release documentation; then verify:

```bash
printf 'N64_INST=%s\n' "${N64_INST:-<unset>}"
command -v mips64-elf-gcc || true
command -v mips64-elf-ld || true
find "${N64_INST:-/nonexistent}" -name n64.mk -print 2>/dev/null
```

Compiler names and layout vary across libdragon toolchain releases. Follow the exact pinned release's documentation rather than assuming the above names are universal. Emulators are a separate dependency and must be installed and verified independently. No boot, ROM compilation or RAM result is claimed by this kit.

## Codex prompt

> Read this README. Locate the user-provided N64 SDK/toolchain parts. Verify the manifest and reconstruct the archive. Install the pinned SDK/compiler only if permitted, verify N64_INST, and compile a minimal libdragon boot-to-menu ROM. If the parts or environment permissions are missing, report the exact blocker. Never claim the compiler is installed simply because this transfer kit exists.
