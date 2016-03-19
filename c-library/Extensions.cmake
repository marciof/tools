if(COMMAND "CMAKE_POLICY")
    cmake_policy(SET CMP0011 OLD)
endif()

if(COMMAND "CMAKE_POLICY")
    cmake_policy(SET CMP0003 NEW)
endif()


set(FALSE 0)
set(TRUE 1)


function(add_check_target TARGET)
    if(MEMORYCHECK_COMMAND)
        set(MEMORY_CHECK_OPTION "-D" "ExperimentalMemCheck")
    else()
        set(MEMORY_CHECK_OPTION "")
    endif()
    
    if(CMAKE_BUILD_TYPE STREQUAL "Debug")
        set(CODE_COVERAGE_OPTION "-D" "ExperimentalCoverage")
    else()
        set(CODE_COVERAGE_OPTION "")
    endif()
    
    add_custom_target("${TARGET}"
        COMMAND ${CMAKE_CTEST_COMMAND}
            "-D" "ExperimentalStart"
            "-D" "ExperimentalTest"
            ${MEMORY_CHECK_OPTION}
            ${CODE_COVERAGE_OPTION}
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
endfunction()


function(add_doxygen_target TARGET DIRECTORY DOXYFILE)
    find_package("Doxygen")
    
    if(NOT DOXYGEN_FOUND)
        warning("Doxygen not found.")
        add_custom_target(${TARGET})
    else()
        get_filename_component(DOXYFILE_OUT ${DOXYFILE} NAME)
        set(DOXYFILE_OUT "${CMAKE_CURRENT_BINARY_DIR}/${DOXYFILE_OUT}.out")
        configure_file(${DOXYFILE} ${DOXYFILE_OUT})
        
        add_custom_target(${TARGET}
            COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYFILE_OUT}
            DEPENDS ${DOXYFILE})
        
        install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/${DIRECTORY}"
            DESTINATION "share/doc/${CMAKE_PROJECT_NAME}")
    endif()
endfunction()


function(add_line_conversion_target TARGET)
    find_program(DOS2UNIX_PROGRAM "dos2unix")
    find_program(FLIP_PROGRAM "flip")
    find_program(SED_PROGRAM "sed")
    
    if(DOS2UNIX_PROGRAM)
        set(PROGRAM ${DOS2UNIX_PROGRAM})
        set(ARGUMENTS)
    elseif(FLIP_PROGRAM)
        set(PROGRAM ${FLIP_PROGRAM})
        set(ARGUMENTS "-u" "-v")
    elseif(SED_PROGRAM)
        set(PROGRAM ${SED_PROGRAM})
        set(ARGUMENTS "-i" "s/\\x0D//")
    endif()
    
    if(PROGRAM)
        add_custom_target(${TARGET} COMMAND ${PROGRAM} ${ARGUMENTS} ${ARGN})
    else()
        warning("Unable to convert lines, no suitable program found.")
    endif()
endfunction()


function(add_line_count_target TARGET)
    set(ERROR_MESSAGE "Unable to count lines")
    
    if(UNIX)
        find_program(CAT_PROGRAM "cat")
        find_program(WC_PROGRAM "wc")
        
        if(CAT_PROGRAM AND WC_PROGRAM)
            add_custom_target(${TARGET}
                COMMAND ${CAT_PROGRAM} ${ARGN} "|" ${WC_PROGRAM} "-l")
        else()
            warning("${ERROR_MESSAGE}: cat/wc not found.")
        endif()
    elseif(WIN32)
        string(REPLACE "/" "\\" FILES "${ARGN}")
        
        add_custom_target(${TARGET}
            COMMAND "type" ${FILES} "2>nul" "|" "find" "/V" "/C" "\"\"")
    else()
        warning("${ERROR_MESSAGE}: Unsupported system.")
    endif()
endfunction()


function(add_package_target TARGET MAJOR MINOR PATCH DESCRIPTION LICENSE_FILE)
    set(VERSION "${MAJOR}-${MINOR}-${PATCH}")
    
    set(CPACK_PACKAGE_NAME ${CMAKE_PROJECT_NAME})
    set(CPACK_PACKAGE_VERSION_MAJOR ${MAJOR})
    set(CPACK_PACKAGE_VERSION_MINOR ${MINOR})
    set(CPACK_PACKAGE_VERSION_PATCH ${PATCH})
    
    if(CYGWIN)
        set(CYGWIN_PHONY_FILE "${CMAKE_CURRENT_BINARY_DIR}/.cygwin")
        file(WRITE ${CYGWIN_PHONY_FILE})
        set(CPACK_CYGWIN_BUILD_SCRIPT ${CYGWIN_PHONY_FILE})
        set(CPACK_CYGWIN_PATCH_FILE ${CYGWIN_PHONY_FILE})
        set(CPACK_CYGWIN_PATCH_NUMBER 0)
    endif()
    
    set(CPACK_NSIS_DISPLAY_NAME "${CPACK_PACKAGE_NAME} ${VERSION}")
    set(CPACK_NSIS_MODIFY_PATH ${TRUE})
    
    set(CPACK_SOURCE_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME} ${VERSION}")
    set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "${DESCRIPTION}")
    set(CPACK_RESOURCE_FILE_LICENSE ${LICENSE_FILE})
    math(EXPR BITS "${CMAKE_SIZEOF_VOID_P} * 8")
    
    set(CPACK_PACKAGE_FILE_NAME
        "${CPACK_PACKAGE_NAME} ${VERSION} (${CMAKE_SYSTEM_NAME}, ${BITS}-bit)")
    
    include("CPack")
    
    add_custom_target("${TARGET}_binary"
        COMMAND ${CMAKE_CPACK_COMMAND} "--config" "CPackConfig.cmake"
        DEPENDS ${LICENSE_FILE}
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
    
    add_custom_target("${TARGET}_source"
        COMMAND ${CMAKE_CPACK_COMMAND} "--config" "CPackSourceConfig.cmake"
        DEPENDS ${LICENSE_FILE}
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
    
    add_custom_target(${TARGET})
    add_dependencies(${TARGET} "${TARGET}_binary" "${TARGET}_source")
endfunction()


function(add_docbook_target TARGET DOCBOOK)
    find_program(BUILD_CATALOG "build-docbook-catalog")
    
    add_xmllint_target("${TARGET}_validate" ${DOCBOOK})
    add_xmlto_target(${TARGET} ${DOCBOOK})
    add_dependencies(${TARGET} "${TARGET}_validate")
    
    if(BUILD_CATALOG)
        file(READ ${BUILD_CATALOG} ROOT_CATALOG)
        regex_match("ROOTCATALOG=([^\n]+)" "${ROOT_CATALOG}" ROOT_CATALOG)
        
        get_filename_component(ROOT_CATALOG_DIR ${ROOT_CATALOG} PATH)
        file(MAKE_DIRECTORY ${ROOT_CATALOG_DIR})
        
        add_custom_command(OUTPUT ${ROOT_CATALOG} COMMAND ${BUILD_CATALOG})
        add_custom_target("${TARGET}_setup" "" DEPENDS ${ROOT_CATALOG})
        add_dependencies("${TARGET}_validate" "${TARGET}_setup")
    endif()
endfunction()


function(add_xmllint_target TARGET XML_FILE)
    find_program(XMLLINT_EXECUTABLE "xmllint")
    
    if(NOT XMLLINT_EXECUTABLE)
        find_package(LibXml2)
        set(XMLLINT_EXECUTABLE ${LIBXML2_XMLLINT_EXECUTABLE})
    endif()
    
    if(NOT XMLLINT_EXECUTABLE)
        warning("xmllint not found.")
        add_custom_target(${TARGET})
    else()
        string(REGEX REPLACE "[ ]" "%20" URI_PATH ${XML_FILE})
        
        add_custom_target(${TARGET}
            COMMAND ${XMLLINT_EXECUTABLE} "--noout" "--valid" ${URI_PATH}
            DEPENDS ${XML_FILE})
    endif()
endfunction()


function(add_xmlto_target TARGET XML_FILE)
    find_program(XMLTO_EXECUTABLE "xmlto")
    
    if(NOT XMLTO_EXECUTABLE)
        warning("xmlto not found.")
        add_custom_target(${TARGET})
    else()
        get_filename_component(HTML_FILE ${XML_FILE} NAME_WE)
        set(HTML_FILE "${CMAKE_CURRENT_BINARY_DIR}/${HTML_FILE}.html")
        
        add_custom_command(
            OUTPUT ${HTML_FILE}
            DEPENDS ${XML_FILE}
            COMMAND ${XMLTO_EXECUTABLE}
            ARGS "--skip-validation"
                 "-o" ${CMAKE_CURRENT_BINARY_DIR}
                 "xhtml-nochunks"
                 ${XML_FILE})
         
        add_custom_target(${TARGET} DEPENDS ${HTML_FILE})
        
        install(FILES ${HTML_FILE}
            DESTINATION "share/doc/${CMAKE_PROJECT_NAME}")
    endif()
endfunction()


function(regex_expand RE OUTPUT)
    string(REGEX REPLACE "\\\\d" "[0-9]" RE "${RE}")
    string(REGEX REPLACE "\\\\s" "[ \r\n\t]" RE "${RE}")
    
    set(${OUTPUT} "${RE}" PARENT_SCOPE)
endfunction()


function(regex_match RE INPUT OUTPUT)
    regex_expand("${RE}" RE)
    
    # Remove escaped groups.
    string(REGEX REPLACE "\\\\[()]" "" GROUPS "${RE}")
    
    # Remove everything except groups.
    string(REGEX REPLACE "[^()]" "" GROUPS "${GROUPS}")
    
    # Count number of groups.
    string(REGEX REPLACE "\\(\\)" "." GROUPS "${GROUPS}")
    string(LENGTH "${GROUPS}" GROUPS)
    
    if(GROUPS GREATER 0)
        # Build group capturing string.
        set(CAPTURE_GROUPS ";")
        foreach(GROUP RANGE 1 ${GROUPS} 1)
            set(CAPTURE_GROUPS "${CAPTURE_GROUPS}\\${GROUP};")
        endforeach()
    else()
        # No capturing groups found, split the string in case there's a match.
        set(CAPTURE_GROUPS ";\\0;")
    endif()
    
    string(REGEX REPLACE "${RE}" "${CAPTURE_GROUPS}" MATCHES "${INPUT}")
    list(LENGTH MATCHES MATCHES_COUNT)
    
    if(GROUPS GREATER 0)
        # Remove match prefix and suffix.
        list(REMOVE_AT MATCHES 0)
        
        while(MATCHES_COUNT GREATER GROUPS)
            list(REMOVE_AT MATCHES -1)
            list(LENGTH MATCHES MATCHES_COUNT)
        endwhile()
    elseif(MATCHES_COUNT EQUAL 1)
        # No matches.
        set(MATCHES)
    else()
        # No capturing groups, return the full input.
        set(MATCHES "${INPUT}")
    endif()
    
    set(${OUTPUT} "${MATCHES}" PARENT_SCOPE)
endfunction()


function(set_tuple)
    math(EXPR PAIRS "${ARGC} / 2 - 1")
    
    foreach(I RANGE ${PAIRS})
        math(EXPR J "${I} + ${PAIRS} + 1")
        
        list(GET ARGN ${I} VAR)
        list(GET ARGN ${J} VALUE)
        
        set(${VAR} "${VALUE}" PARENT_SCOPE)
    endforeach()
endfunction()


function(warning MESSAGE)
    message(STATUS "Warning: ${MESSAGE}")
endfunction()


if(CMAKE_VERSION STRLESS "2.8")
    find_program(VALGRIND_PROGRAM "valgrind")
    
    if(VALGRIND_PROGRAM)
        set(MEMORYCHECK_COMMAND_OPTIONS
            "-q --tool=memcheck --leak-check=yes --show-reachable=yes")
        warning("Fixed Valgrind command line options.")
    endif()
endif()


regex_match("\\s" ${CMAKE_BINARY_DIR} HAS_WHITE_SPACE)

if(HAS_WHITE_SPACE)
    warning("White-space found in CMAKE_BINARY_DIR, possible build failures.")
endif()

enable_testing()
include("CTest")
