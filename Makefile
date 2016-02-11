CPPFLAGS=-ansi -pedantic-errors -Wall -O2 -g
LDFLAGS=-lutil

show: show.cpp
	$(CXX) $(CPPFLAGS) -o $@ $< $(LDFLAGS)
