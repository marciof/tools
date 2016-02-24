cmake_minimum_required(VERSION 3.4)
project(show C)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

if(CMAKE_COMPILER_IS_GNUCC)
    add_compile_options(-std=c99 -pedantic-errors -Wall -O2)
endif()

set(libraries m util)
file(GLOB_RECURSE sources src/*.c src/*.h)
file(GLOB_RECURSE tests test/*.c test/*.h)

add_executable(${PROJECT_NAME} ${sources})
target_link_libraries(${PROJECT_NAME} ${libraries})

add_executable("${PROJECT_NAME}-test" ${tests})
target_link_libraries("${PROJECT_NAME}-test" check rt pthread ${libraries})
target_include_directories("${PROJECT_NAME}-test" PUBLIC src/)
