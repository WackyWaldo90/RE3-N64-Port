# RE3 Classic Toolkit — Codex Workflow Pack

This pack is a safe starter workflow for WackyWaldo90/RE3-N64-Port. Copy `AGENTS.md`, `scripts/` and `.github/workflows/` to the root of that repository.

## Verified Drive installer
- Name: Resident-Evil-Classic-Toolkit-v1.1.0-CORREGIDO-Setup-x64.exe
- Size: 213,535,958 bytes
- SHA-256: `f903d00d0d096c1b22bf4892185491c76bf2e592fe7d1c14b785ae824fa8d52f`
- Source: Google Drive / Tools
- Format: Windows PE32+ x64 executable.

The installer was inspected **statically only**. Its embedded contents and actual feature set have not been verified. Strings resembling Electron, NSIS, RDT, EMD and SCD occur in the binary; these do not prove supported functionality.

## Workflow
1. Retain installer in Drive. Avoid public redistribution.
2. On a trusted isolated Windows analysis VM, inspect the installer and export permitted documentation and data; do not execute unknown software in GitHub Actions.
3. Use `python scripts/toolkit_pipeline.py inventory exported-directory reports` to create a hashed inventory.
4. Curate small textual format specs and JSON/CSV catalogues for Codex, with exact source provenance.
5. Use `python scripts/toolkit_pipeline.py split approved-file.bin parts` only if distributing the file is authorized. Each part is 24,000,000 bytes (below 25,000,000 bytes); manifest records hashes.
6. Use `python scripts/toolkit_pipeline.py restore parts rebuilt-file.bin` to reconstruct and verify it.
7. Run the workflow in GitHub Actions to test the pipeline without requiring ROMs or the installer.

## Next research deliverables
- `reports/toolkit_modules.json`: verified module inventory (not yet generated)
- `reports/re3_format_catalogue.json`: PS1 format evidence (not yet generated)
- `reports/re2_n64_comparison.csv`: verified RE2 vs RE3 format/size mapping (not yet generated)
- `reports/ram_budget.md`: measured N64 runtime allocations (not yet generated)

**Important:** Splitting an installer does not reduce its total storage or make it useful to Codex as source code. The most useful output is a compact, evidence-backed reference catalogue. GitHub's actual individual file limits differ by upload method; 24 MB chunks are a conservative target, not a universal GitHub limit.
