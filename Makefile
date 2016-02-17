CXXFLAGS=-ansi -pedantic-errors -Wall
LDFLAGS=-lutil

show: show.cpp std/string.c
	$(CXX) $(CXXFLAGS) -O2 -g -o $@ $^ $(LDFLAGS)
