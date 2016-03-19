cmake_minimum_required(VERSION 2.8)
project(show C)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

if(CMAKE_COMPILER_IS_GNUCC)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c99 -pedantic-errors -Wall -Wextra -Wno-unused-parameter -O2")
endif()

set(sources
    src/Array.c
    src/Array.h
    src/plugin/Pipe_Plugin.c
    src/plugin/Pipe_Plugin.h
    src/plugin/Ls_Plugin.c
    src/plugin/Ls_Plugin.h
    src/Error.c
    src/Error.h
    src/options.c
    src/options.h
    src/plugin/File_Plugin.c
    src/plugin/File_Plugin.h
    src/plugin/Pager_Plugin.c
    src/plugin/Pager_Plugin.h
    src/plugin/Plugin.c
    src/plugin/Plugin.h
    src/fork_exec.c
    src/fork_exec.h)

add_executable(${PROJECT_NAME}
    ${sources}
    src/main.c)

add_executable(${PROJECT_NAME}-test
    ${sources}
    test/main.test.c
    test/Array.test.c
    test/Array.test.h)

set(libraries util)
target_link_libraries(${PROJECT_NAME} ${libraries})
target_link_libraries(${PROJECT_NAME}-test check m pthread rt ${libraries})

target_include_directories(${PROJECT_NAME}-test PUBLIC src/)
