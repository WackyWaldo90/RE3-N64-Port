# RE3 N64 Milestone 120 — ROM collision bank prototype

Build bank: `python build_collision_bank.py n64_collision rom_bank`

Host C test: `gcc -std=c99 -O2 -Wall -Wextra -Werror r3sc_loader.c r3sc_manager.c r3sc_bank.c test_r3sc_bank.c -o test_r3sc_bank && ./test_r3sc_bank rom_bank/collision_index.bin rom_bank/collision_bank.bin`

Run Python tests: `python -m unittest discover -s . -p "test_*.py"`

The ROM bank is a **project-defined intermediate container**, not an actual N64 ROM. Loader operates on in-memory bytes and does not implement PI DMA, libultra/libdragon, RE3 engine collision behavior, or hardware validation.
