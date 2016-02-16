CXXFLAGS=-ansi -pedantic-errors -Wall
LDFLAGS=-lutil

show: show.cpp
	$(CXX) $(CXXFLAGS) -O2 -g -o $@ $^ $(LDFLAGS)
