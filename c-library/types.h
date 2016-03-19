#ifndef __EON__LIBRARY__TYPES__
#define __EON__LIBRARY__TYPES__


/**
 * @file
 * @brief Core data types
 *
 * Includes header files for commonly used types, defines fixed width integral
 * types and defines a boolean data type.
 */


#include <stddef.h>
#include "util.h"


#if defined(__GNUC__) || defined(_POSIX_VERSION)
#   include <sys/types.h>
#else
    /** Signed size_t. */
    typedef ptrdiff_t ssize_t;
#endif


#if C_STANDARD >= 199901L
#   include <inttypes.h>
#   include <stdbool.h>
#else
#   if defined(__GNUC__)
        /* Suppress warning: ISO C90 does not support "long long". Also use
           #pragma instead of PRAGMA to affect files that use this header. */
        #pragma GCC system_header
#   endif
    
#   ifndef _STDINT_H
        /**
         * @name Fixed width integral types
         * @{
         */
#       ifdef _MSC_VER
            typedef signed __int8 int8_t;
            typedef signed __int16 int16_t;
            typedef signed __int32 int32_t;
            typedef signed __int64 int64_t;
            
            typedef unsigned __int8 uint8_t;
            typedef unsigned __int16 uint16_t;
            typedef unsigned __int32 uint32_t;
            typedef unsigned __int64 uint64_t;
#       else
#           ifndef __int8_t_defined
#               define __int8_t_defined
                
                /** Signed 8 bits integral type. */
                typedef signed char int8_t;
                
                /** Signed 16 bits integral type. */
                typedef signed short int16_t;
                
                /** Signed 32 bits integral type. */
                typedef signed int int32_t;
                
                /** Signed 64 bits integral type. */
                typedef signed long long int64_t;
#           endif
            
            /** Unsigned 8 bits integral type. */
            typedef unsigned char uint8_t;
            
            /** Unsigned 16 bits integral type. */
            typedef unsigned short uint16_t;
            
            /** Unsigned 32 bits integral type. */
            typedef unsigned int uint32_t;
            
            /** Unsigned 64 bits integral type. */
            typedef unsigned long long uint64_t;
#       endif
        /* @} */
#   endif
    
    STATIC_ASSERT(sizeof(int8_t) == 1, "Invalid int8_t size.");
    STATIC_ASSERT(sizeof(uint8_t) == 1, "Invalid uint8_t size.");
    STATIC_ASSERT(sizeof(int16_t) == 2, "Invalid int16_t size.");
    STATIC_ASSERT(sizeof(uint16_t) == 2, "Invalid uint16_t size.");
    STATIC_ASSERT(sizeof(int32_t) == 4, "Invalid int32_t size.");
    STATIC_ASSERT(sizeof(uint32_t) == 4, "Invalid uint32_t size.");
    STATIC_ASSERT(sizeof(int64_t) == 8, "Invalid int64_t size.");
    STATIC_ASSERT(sizeof(uint64_t) == 8, "Invalid uint64_t size.");
    
#   if !defined(__cplusplus) && !defined(_STDBOOL_H)
        /** Boolean data type. */
        typedef uint8_t bool;
        
        enum {
            /** Falsehood boolean value. */
            false = 0,
            
            /** Truth boolean value. */
            true = !false
        };
#   endif
#endif


#endif
