# Codex instructions — RE3 N64 prototype

This repository contains a verified M120 host-side collision/bank research milestone, **not** a playable ROM. Do not invent build, emulator, PS1 trace, or gameplay test results.

## Work order and acceptance gates
1. **Phase A — workspace/toolchain:** inspect the repository; run `make test`; document errors; configure a reproducible open-source N64 toolchain (prefer libdragon) with pinned versions; build a minimal bootable ROM; boot it in an available emulator and record the exact command, log and screenshot where possible. Do not claim completion without actual evidence.
2. **Phase B — rooms:** establish a renderer with placeholder graphics and fixed camera, then integrate appropriately licensed RE3 room assets only if available. Show two rooms.
3. **Phase C — player:** implement tank movement, animation state machine and controller mapping, using placeholders until approved model assets are available.
4. **Phase D — collision/stairs:** port and test M120 R3SC loading/room management; implement collision solver and stair traversal separately. Confirm host tests and emulator behavior.
5. **Phase E — transitions:** add room doors, camera transitions, spawn points, repeated-entry stability.
6. **Phase F — demo features:** enemy, basic combat, inventory, audio and saves, one feature at a time, with tests.

## Constraints
- Preserve source provenance and avoid uploading commercial disc images or unauthorized copyrighted game assets.
- M120 `rom_bank` is a **host-memory bank prototype**, not N64 DMA integration.
- Keep C99 host code portable, isolate N64 APIs, measure memory and ROM budget.
- Report file changes, test commands, pass/fail, emulator evidence, blockers after each phase.
- Begin with Phase A only; never claim a playable demo until one boots and runs.
