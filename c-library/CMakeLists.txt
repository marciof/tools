project("Eon" C CXX)
cmake_minimum_required(VERSION 2.6)
include("${CMAKE_CURRENT_SOURCE_DIR}/Extensions.cmake")

file(READ "${CMAKE_CURRENT_SOURCE_DIR}/properties.h" PROPERTIES_H)
regex_match("_VERSION\\s(....)(..)(..)L" "${PROPERTIES_H}" CMAKE_PROJECT_VERSION)
set_tuple(YEAR MONTH DAY ${CMAKE_PROJECT_VERSION})
set(CMAKE_PROJECT_VERSION "${YEAR}-${MONTH}-${DAY}")

# ------------------------------------------------------------------------------

if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX)
    add_definitions("-ansi" "-pedantic" "-Wall" "-Wextra" "-Wredundant-decls"
        "-Wshadow" "-Wswitch-default" "-Wundef" "-Wunused-macros")
    
    set(OPTIONS "-fprofile-arcs -ftest-coverage")
    
    set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} ${OPTIONS}")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} ${OPTIONS}")
    set(CMAKE_LINKER_FLAGS "${CMAKE_LINKER_FLAGS} ${OPTIONS}")
endif()

set(EXECUTABLE_OUTPUT_PATH ${CMAKE_CURRENT_BINARY_DIR})
set(LIBRARY_OUTPUT_PATH ${CMAKE_CURRENT_BINARY_DIR})

file(GLOB_RECURSE FILES "*.[ch]")
add_line_conversion_target("convert_lines" ${FILES})
add_line_count_target("count_lines" ${FILES})

# ------------------------------------------------------------------------------

file(GLOB_RECURSE SOURCE_FILES "*.[ch]")

foreach(SOURCE_FILE ${SOURCE_FILES})
    regex_match("test[.][ch]" ${SOURCE_FILE} IS_TEST)
    
    if(IS_TEST)
        list(REMOVE_ITEM SOURCE_FILES ${SOURCE_FILE})
    endif()
endforeach()

add_library("shared_library" SHARED ${SOURCE_FILES})
add_library("static_library" STATIC ${SOURCE_FILES})

add_custom_target("library")
add_dependencies("library" "static_library" "shared_library")

set_target_properties("shared_library" PROPERTIES
    COMPILE_FLAGS "-DPUBLIC_API=PUBLIC_EXPORT")

set_target_properties("shared_library" "static_library" PROPERTIES
    OUTPUT_NAME ${CMAKE_PROJECT_NAME}
    CLEAN_DIRECT_OUTPUT ${TRUE}
    SOVERSION ${CMAKE_PROJECT_VERSION}
    VERSION ${CMAKE_PROJECT_VERSION})

if(WIN32)
    set_target_properties("shared_library" "static_library" PROPERTIES
        PREFIX "")
    
    if(MSVC)
        set_target_properties("shared_library" PROPERTIES
            IMPORT_SUFFIX ".import.lib")
    endif()
endif()

if(FORCE_CPP)
    set_source_files_properties(${SOURCE_FILES} PROPERTIES LANGUAGE CXX)
    set_target_properties("shared_library" "static_library" PROPERTIES
        LINKER_LANGUAGE CXX)
endif()

if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX)
    if(CMAKE_BUILD_TYPE STREQUAL "Debug")
        target_link_libraries("shared_library" "gcov")
    endif()
    
    target_link_libraries("shared_library" "m")
    target_link_libraries("static_library" "m")
endif()

install(TARGETS "shared_library" "static_library"
    ARCHIVE DESTINATION "lib"
    LIBRARY DESTINATION "lib"
    RUNTIME DESTINATION "lib")

install(DIRECTORY "." DESTINATION "include/${CMAKE_PROJECT_NAME}"
    PATTERN ".svn" EXCLUDE
    PATTERN "*.c" EXCLUDE
    PATTERN "*.txt" EXCLUDE)

# ------------------------------------------------------------------------------

file(GLOB_RECURSE TEST_FILES "*.test.c")

if(FORCE_CPP)
    set_source_files_properties(${TEST_FILES} PROPERTIES LANGUAGE CXX)
endif()

add_check_target("check")
add_custom_target("tests")
link_directories(${CMAKE_BINARY_DIR})

foreach(TEST_SOURCE ${TEST_FILES})
    file(RELATIVE_PATH TEST ${CMAKE_CURRENT_SOURCE_DIR} ${TEST_SOURCE})
    string(REGEX REPLACE "[.]c$" "" TEST ${TEST})
    string(REGEX REPLACE "/" "." TEST ${TEST})
    
    set(TEST_STATIC "${TEST}.static")
    set(TEST_SHARED "${TEST}.shared")
    
    add_executable(${TEST_STATIC} ${TEST_SOURCE})
    add_executable(${TEST_SHARED} ${TEST_SOURCE})
    
    set_target_properties(${TEST_SHARED} PROPERTIES
        COMPILE_FLAGS "-DPUBLIC_API=PUBLIC_IMPORT")
    
    target_link_libraries(${TEST_STATIC} "static_library")
    target_link_libraries(${TEST_SHARED} "shared_library")
    
    add_test(${TEST_STATIC} "${CMAKE_BINARY_DIR}/${TEST_STATIC}")
    add_test(${TEST_SHARED} "${CMAKE_BINARY_DIR}/${TEST_SHARED}")
    
    add_dependencies("tests" ${TEST_STATIC} ${TEST_SHARED})
    add_dependencies("check" ${TEST_STATIC} ${TEST_SHARED})
    
    if(FORCE_CPP)
        set_target_properties(${TEST_STATIC} PROPERTIES LINKER_LANGUAGE CXX)
        set_target_properties(${TEST_SHARED} PROPERTIES LINKER_LANGUAGE CXX)
    endif()
endforeach()

# ------------------------------------------------------------------------------

add_package_target("installer" ${YEAR} ${MONTH} ${DAY}
    "Software library to ease development in the C programming language."
    "${CMAKE_CURRENT_SOURCE_DIR}/../License.txt")

file(GLOB DOCUMENTS "*.txt" "*.csv")
install(FILES ${DOCUMENTS} DESTINATION "share/doc/${CMAKE_PROJECT_NAME}")

add_custom_target("docs")
add_dependencies("docs" "docs_api")

add_dependencies("installer_binary" "library" "docs")

add_custom_target("release")
add_dependencies("release" "check" "installer")
