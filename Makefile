CFLAGS=-std=c99 -pedantic-errors -Wall
LDFLAGS=-lm -lutil

show: src/*.c src/*/*.c
	$(CC) $(CFLAGS) -O2 -g -o $@ $^ $(LDFLAGS)
