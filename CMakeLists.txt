cmake_minimum_required(VERSION 2.6)
project(show C)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

if(CMAKE_COMPILER_IS_GNUCC)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c99 -pedantic-errors -Wall -Wextra -Wno-unused-parameter -O2")
endif()

add_executable(${PROJECT_NAME}
    src/Array.c
    src/Array.h
    src/plugin/Stdin.c
    src/plugin/Stdin.h
    src/plugin/Dir.c
    src/plugin/Dir.h
    src/plugin/Vcs.c
    src/plugin/Vcs.h
    src/Error.c
    src/Error.h
    src/options.c
    src/options.h
    src/plugin/File.c
    src/plugin/File.h
    src/plugin/Pager.c
    src/plugin/Pager.h
    src/Plugin.c
    src/Plugin.h
    src/popen2.c
    src/popen2.h
    src/io.c
    src/io.h
    src/main.c)

target_link_libraries(${PROJECT_NAME} pthread util)

add_executable(pty src/pty.c)
target_link_libraries(pty util)
