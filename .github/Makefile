CC ?= cc
CFLAGS ?= -std=c99 -O2 -Wall -Wextra -Werror
.PHONY: test clean
test: test_r3sc_manager
	./test_r3sc_manager n64_collision/R100.r3sc n64_collision/R101.r3sc
	python3 -m unittest discover -s . -p 'test_*.py'
test_r3sc_manager: r3sc_loader.c r3sc_loader.h r3sc_manager.c r3sc_manager.h test_r3sc_manager.c
	$(CC) $(CFLAGS) r3sc_loader.c r3sc_manager.c test_r3sc_manager.c -o $@
clean:
	rm -f test_r3sc_manager
