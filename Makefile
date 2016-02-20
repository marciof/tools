CXXFLAGS=-std=c99 -pedantic-errors -Wall -Wno-conversion-null
LDFLAGS=-lutil

show: src/*.cpp src/*/*.c
	$(CXX) $(CXXFLAGS) -O2 -g -o $@ $^ $(LDFLAGS)
