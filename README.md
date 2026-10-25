# RE3 N64 Port: GitHub Actions Toolchain Pack

Copy `.github/workflows/*.yml` and `scripts/*` into the corresponding paths in `WackyWaldo90/RE3-N64-Port`. Commit them, then use GitHub Actions > Run workflow. The pack does **not** contain or install proprietary Nintendo SDKs, ROMs, or game assets.

- `reverse-engineering-tools.yml`: create a Python environment and attempt installation/import checks for splat, spimdisasm, rabbitizer, n64img. Errors are logged; package naming/version changes may require adjustments.
- `n64-build-toolchain.yml`: check Docker and fetch libdragon source, inventory project build inputs. **Does not claim to compile the game or install an N64 compiler.**
- `media-analysis-tools.yml`: install FFmpeg, 7-Zip and binary utilities; archive version information.
- `rom-inventory.yml`: validate a Python ROM inventory script; skip cleanly unless a private ROM is supplied to `private-input/re2.z64` on the runner. Do not commit copyrighted ROM files to public GitHub.

The existing `ares-flatpak.yml` workflow remains separate. Ares GUI operation and automated gameplay require a virtual display, test inputs, verified ROM delivery and screenshots, and are **not** implemented here.

GitHub-hosted runners are ephemeral. Forked source repositories are not installed automatically. For reproducible results, pin tool versions/commit SHAs after first successful CI run. Review workflow logs and fix dependencies rather than assuming a green check proves functional game extraction.
