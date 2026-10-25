# M120 investigation and results

Verified M119 uploaded in Google Drive; RE3 Europe BIN (712,491,360 bytes) present in Dropbox; Bio3 SCA definitions checked in MeganGrass/bio-lib on GitHub. Full PS1 BIN remains unavailable to local executable tracing.

New reproducible engineering deliverables:
- `build_collision_bank.py` verifies each R3SC file and packs 168 nonempty rooms into a single 16-byte aligned ROM-style data bank.
- `rom_bank/collision_index.bin` is big-endian R3BK v1 index: 16-byte header with magic, version, room count, bank byte length, bank CRC32; each 28-byte entry contains zero-padded 16-byte room name, offset, length, per-file CRC32.
- `rom_bank/collision_bank.bin` contains the 168 source room files unmodified with alignment padding.
- `r3sc_bank.c/.h` validates index, bank CRC, per-room CRC and offsets, then activates the selected room atomically using M119 manager.
- `test_r3sc_bank.c` checks successful activation and preservation of active room after missing room/corrupt bank.

Important: A host-memory bank loader is **not yet** an N64 DMA/ROM loader, nor an RE3 collision solver. Need N64 toolchain/ROM build and emulator tests; actual RE3 CPU traces are still pending.

References: https://github.com/MeganGrass/bio-lib/blob/main/Bio3/SCA/bio3_sca.h ; https://github.com/grumpycoders/pcsx-redux
