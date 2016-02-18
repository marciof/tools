CXXFLAGS=-ansi -pedantic-errors -Wall
LDFLAGS=-lutil

show: src/show.cpp src/std/string.c
	$(CXX) $(CXXFLAGS) -O2 -g -o $@ $^ $(LDFLAGS)
