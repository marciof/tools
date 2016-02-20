CFLAGS=-std=c99 -pedantic-errors -Wall -O2
LDFLAGS=-lm -lutil
DEBUG?=0

ifeq ($(DEBUG), 1)
    CFLAGS:=$(CFLAGS) -g
endif

show: src/*.c src/*/*.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
