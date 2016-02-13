CPPFLAGS=-ansi -pedantic-errors -Wall
LDFLAGS=-lutil

show: show.cpp
	$(CXX) $(CPPFLAGS) -O2 -g -o $@ $^ $(LDFLAGS)
