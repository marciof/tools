CXXFLAGS=-std=c++11 -pedantic-errors -Wall
LDFLAGS=-lutil

show: show.cpp
	$(CXX) $(CXXFLAGS) -O2 -g -o $@ $^ $(LDFLAGS)
