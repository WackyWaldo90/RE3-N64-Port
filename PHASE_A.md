# Phase A recovery report — 2026-10-25

**Outcome: workspace recovered and host baseline exercised; Phase A acceptance is not complete. Phase B is blocked.**

No bootable ROM was built or emulated. Five remote archives could not be downloaded
for integrity testing. The N64 SDK/compiler and emulator are missing. This report
records those limitations rather than treating audit completion as prototype completion.

## A1 — Repository and source audit

- Initial `/workspace` had no checkout, source files or uploaded milestone archives.
- Inspected `NETWORK_SETUP.md` through GitHub. `/home/agent/.codex/config.toml` is empty; `/workspace/.codex/config.toml` and the effective CODEX_HOME config are absent.
- Recovered the workspace archive through the GitHub connector at commit `d1e1e144f1bdd85ce53d55eda5d720402eabc5a9`. No additional clone was attempted after the user's diagnostic instruction.
- Remote GitHub inventory contains 105 file/directory entries. Most unpacked files were misplaced directly in `.github`; the ZIP contains the intended structured workspace.
- Recursively inventoried all accessible `VG` folders: 21 entries. `VG/Emulators` is empty; the folder named `RE3 N64 Base.z64` contains a README, not a ROM binary. Tools contains manuals/licenses rather than an installed toolchain.
- Recursively inventoried the approved Dropbox project subtree: 1,755 entries, comprising 1,067 files and 688 folders, across three fully consumed pages.
- Recovered a work copy at `/workspace/re3-n64`; preserved archive/extraction at `/workspace/recovery`. Also recovered 25 Dropbox legacy text/source files with provider IDs. Dropbox text extraction does not establish byte-for-byte binary provenance.
- Initialized a local `recovery` Git branch with no commits or staged files. This is not an upstream checkout or imported history. Source tracking comes from the remote inventory; `git-status.txt` and `git-tracked.txt` record local state.

Evidence: `source-inventory.json`, `network-audit.json`, preserved provider listings and original ZIP.

## A2–A3 — Archive validation and safe extraction

| Archive | Location | Bytes | Result |
| --- | --- | ---: | --- |
| RE3%20Codex%20Workspace.zip | GitHub | 392,652 | Validated and safely extracted |
| ares-source.tar.gz | Dropbox | 5,465,693 | Blocked: remote-only |
| universal-modder-main.zip | Dropbox | 24,879,779 | Blocked: remote-only |
| Resident Evil 2 (Europe) (Disc 1) (1).zip | Dropbox | 394,401,928 | Blocked: remote-only |
| unar-master.zip | Dropbox | 2,533,608 | Blocked: remote-only |
| RE3_Staircase_Integration_v1.zip | Dropbox | 4,675 | Blocked: remote-only |

The recovered ZIP has SHA-256
`9b8bf1d6b1dc01d16942bfc8291bcc636db22708d4ce36dff45de041f2e91054`.
Its Git blob hash matched `c07932902e8a1a85202494eada48c0e305d288b4`.
All 223 entries (951,172 expanded bytes) passed streamed CRC and safety checks;
all 222 supplied per-file SHA-256 hashes matched. No encrypted entries, unsafe
paths, symlinks or LFS pointers were found in that ZIP.

No split archive, RAR or 7z filename was found in accessible inventories. Remote
signatures, encryption and LFS contents remain unknown. N64 `.z64` ROM files
were excluded from split-ZIP detection. No integrity or checksum result is
claimed for any remote-only archive. No remote source supplied an archive-level
checksum in the accessible metadata. No files were executed during extraction.

Evidence: `archive-matrix.json`, `archive-validation.json`, `manifest-validation.json`.

## A4 — Resource classification

| Category | Available evidence / limitation |
| --- | --- |
| PS1 RE3 game data | Dropbox Europe BIN (712,491,360 bytes) and CUE metadata; not downloaded or executed |
| PS1 RE2 reference data | Dropbox Europe Disc 1 ZIP metadata; not downloaded |
| N64 RE2 reference data | Engineering PDFs; no actual RE2 N64 ROM identified in these listings |
| C/C++ source | M120 loader/manager/bank and tests; legacy RE-Base and Pyrite64 source |
| Python scripts | Collision QA/packing/bank building; RAM scans, disassembly, PS-X EXE and ISO utilities |
| Emulator configuration | PCSX-Redux/Ares-related metadata; no installed emulator verified |
| Engineering guides | RE3 research manual, RE2 conversion reference, PS1-to-N64 guides and milestone notes |
| Build libraries | CPython, third-party and modding/unarchiver metadata; no libdragon SDK installation |
| Audio/video tools | jPSXdec manual and related references; converted media payloads in legacy metadata |
| Experiments | M120 collision bank, legacy Jill/render/collision/stair and Pyrite64 source |

Classification is based on paths/extensions where contents remain remote. It
does not establish that every referenced tool or game asset is usable.

## A5–A6 — Tools and build results

Working: GCC 14.2.0, GNU Make 4.4.1, Python 3.12.14, Git 2.52.0, PyYAML 6.0.3.
The actual M120 build uses C99 plus standard-library Python; its required host
dependencies were already installed. No dependency installation was necessary.

Missing: libdragon headers/libraries and `n64.mk`, MIPS N64 compiler, ROM tools,
Ares/Mupen64Plus/RetroArch, 7z/unrar backends and actionlint. The supplied legacy
Makefile identifies libdragon via `N64_INST`. Its `make -n` exits 2 with:

```text
Makefile:4: /include/n64.mk: No such file or directory
make: *** No rule to make target '/include/n64.mk'. Stop.
```

No SDK version has been installed or verified. Shell network access needs an
approved per-command grant or host/session permission; a repository TOML cannot
override the managed sandbox. The GitHub/Drive/Dropbox connector reads succeeded.
No blocked network commands were repeatedly retried.

Evidence: `toolchain.json`, `legacy-results.json`, `logs/legacy-n64-make.log`.

## A7 — Automation validation

- Both YAML definitions parse successfully; the archive workflow's embedded Python also parses. Actionlint/full Actions schema validation remains blocked by its absence.
- Root `re3-n64-workspace.yml` is not discovered by GitHub. Its intended manual/push triggers cannot run there.
- Active `.github/workflows/c-cpp.yml` calls absent root `./configure`, Makefile/check/distcheck targets and therefore does not test M120 correctly.
- Archive detection misses split sets and tar.gz; push paths also miss case variants. Archive testing precedes entry/resource validation; encryption can wait for input. Supplied checksums and LFS pointers are not checked.
- Positive controls in the inactive audit definition: read-only contents permission, no persisted checkout credentials, job/subprocess timeouts, report-only artifacts, always-run report steps and 14-day retention.
- Actions use mutable version tags. No remote workflow was triggered and no workflow execution/artifact success is claimed. Findings are recorded; upstream workflows were not modified.

Evidence: `workflow-audit.json`, `logs/workflow-audit.log`.

## A8 — Development structure and changes

Recovered the supplied Makefiles, C/Python modules, tests, docs and local collision
data. Added only needed `tools/`, `scripts/`, `tests/`, `docs/engineering/`, `build/`
and `reports/` structure. Added bounded archive recovery/inventory tools, synthetic
tests, baseline/workflow collectors, engineering recovery notes and an evidence
ledger. Added `make doctor`, `make test-recovery` and `make audit`; retained the
original `make test` target. Expanded ignore rules for archives and derived assets.

Historical input/extraction remain unchanged. No game-source code, collision
format or gameplay behavior was altered. No assets were staged, committed or
uploaded. No remote repository changes were made.

## A9 — Baseline testing

| Check | Result |
| --- | --- |
| Recovered root `make test` | Passed: C manager and 18 Python tests |
| Separate M120 loader, manager and bank programs | All three compile and pass with C99, `-Wall -Wextra -Werror` |
| Legacy collision and stair programs | Both compile and pass |
| Recovery safety/inventory tests | 20 passed |
| All recovered M120 Python source syntax | Passed |
| Repack every nonempty room | All 168 files match, totaling 5,291 records |
| Rebuild ROM-style bank/index | Byte-identical: 87,344 / 4,720 bytes |
| Collision QA | Passed expected nine observations |
| ASan/UBSan manager and loader, leaks disabled | Passed tested paths |
| LeakSanitizer | Blocked: sandbox ptrace restriction causes fatal error |
| GCC analyzer, actual object compilation | Manager/bank pass; loader fails with allocation/null diagnostics at both O2 and O0 |
| Existing JSON validation | Failed: `milestones/M120/n64_collision/manifest.json` has literal trailing `\n` |
| Existing `make clean` | Passed in isolated baseline copy |
| N64 build/emulator | Blocked; no ROM or boot evidence |

The initial GCC syntax-only invocation passed but was insufficient for analyzer
coverage; the actual `-fanalyzer -c` results above supersede that preliminary
check. Loader analyzer traces appear to traverse incompatible count/null branches,
but they are retained as unresolved diagnostics, not suppressed or treated as
proven defects. Separately, the loader resets an output room before validation;
callers must avoid reusing a live room without freeing its records. The original
loader corruption test reuses that output. Ownership/leak behavior needs dedicated
follow-up with working leak instrumentation; no leak-free claim is made.

The JSON issue comes from writing a literal backslash-n in the supplied packer.
The baseline source and historical file were preserved for review.

The largest room contains 75 records, representing 1,200 record bytes under the
16-byte representation. This is a data-size observation, not measured N64 RAM.
ROM size and runtime N64 RAM are unmeasured because no ROM ran.

Evidence: `baseline-results.json`, `legacy-results.json`, detailed `logs/`.

## A10 — Acceptance and readiness

- Accessible archive candidates inventoried: **yes**, six; five binary signatures/integrity tests blocked.
- Archive validation outcomes recorded: **yes**, including unknown/blocked outcomes.
- Required build tools identified: **yes**; host available, N64 missing.
- Existing recovered tests executed or blockers documented: **yes**.
- Milestone ledger updated: **yes**, `docs/engineering/MILESTONES.md`.
- Copyrighted extracted assets committed: **none**; no commits were created.
- Ready for Phase B: **no**. No N64 build/boot acceptance test has passed.

Next work is to grant shell network access (or supply dependencies locally),
validate remaining archives, resolve the loader/manifest findings, establish a
pinned libdragon build and capture a fresh minimal-ROM emulator boot. Missing
individual milestone archives and original RDTs remain explicit evidence gaps.
Stop here; no Phase B implementation was started.
