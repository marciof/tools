cmake_minimum_required(VERSION 3.4)
project(show C)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

if(CMAKE_COMPILER_IS_GNUCC)
    add_compile_options(
        -std=c99 -pedantic-errors -Wall -Wextra -Wno-unused-parameter -O2)
endif()

add_executable(${PROJECT_NAME}
    src/iterator/Iterator.c src/iterator/Iterator.h src/list/Array_List.c
    src/list/Array_List.h src/list/Linked_List.c src/list/Linked_List.h
    src/list/List.c src/list/List.h src/map/Hash_Map.c src/map/Hash_Map.h
    src/map/Map.c src/map/Map.h src/plugin/Pipe_Plugin.c
    src/plugin/Pipe_Plugin.h src/plugin/Ls_Plugin.c src/plugin/Ls_Plugin.h
    src/plugin/Plugin.h src/std/array.h src/std/Error.h src/std/string.c
    src/std/string.h src/main.c src/Options.c src/Options.h
    src/plugin/File_Plugin.c src/plugin/File_Plugin.h src/plugin/Plugin.c)

add_executable(${PROJECT_NAME}-test
    src/iterator/Iterator.c src/iterator/Iterator.h src/list/Array_List.c
    src/list/Array_List.h src/list/Linked_List.c src/list/Linked_List.h
    src/list/List.c src/list/List.h src/map/Hash_Map.c src/map/Hash_Map.h
    src/map/Map.c src/map/Map.h src/plugin/Pipe_Plugin.c
    src/plugin/Pipe_Plugin.h src/plugin/Ls_Plugin.c src/plugin/Ls_Plugin.h
    src/plugin/Plugin.h src/std/array.h src/std/Error.h src/std/string.c
    src/std/string.h src/Options.c src/Options.h
    src/plugin/File_Plugin.c src/plugin/File_Plugin.h src/plugin/Plugin.c
    test/main.test.c test/std/array.test.c test/std/array.test.h
    test/std/string.test.c test/std/string.test.h)

set(libraries m util)
target_link_libraries(${PROJECT_NAME} ${libraries})
target_link_libraries(${PROJECT_NAME}-test check rt pthread ${libraries})

target_include_directories(${PROJECT_NAME}-test PUBLIC src/)
