cmake_minimum_required(VERSION 2.6)
project(show C)

if(CMAKE_COMPILER_IS_GNUCC)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c99 -pedantic-errors -Wall -Wextra -Wno-unused-parameter")
endif()

add_executable(${PROJECT_NAME}
    src/Error.c
    src/Error.h
    src/Array.c
    src/Array.h
    src/Buffer.c
    src/Buffer.h
    src/options.c
    src/options.h
    src/io.c
    src/io.h
    src/popen2.c
    src/popen2.h
    src/Plugin.c
    src/Plugin.h
    src/plugin/Stdin.c
    src/plugin/Stdin.h
    src/plugin/Dir.c
    src/plugin/Dir.h
    src/plugin/Vcs.c
    src/plugin/Vcs.h
    src/plugin/File.c
    src/plugin/File.h
    src/plugin/Pager.c
    src/plugin/Pager.h
    src/main.c)

target_link_libraries(${PROJECT_NAME} pthread util)
