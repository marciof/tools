cmake_minimum_required(VERSION 2.6)
project(show C)

if(CMAKE_COMPILER_IS_GNUCC)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c99 -pedantic-errors -Wall -Wextra -Wno-unused-parameter -O2")
endif()

add_executable(pty src/pty.c)
target_link_libraries(pty util)
