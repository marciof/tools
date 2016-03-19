#ifndef __EON__LIBRARY__UTIL__
#define __EON__LIBRARY__UTIL__


/**
 * @file
 * @brief Standard and compiler dependent definitions
 *
 * Contains useful definitions that usually depend on the current C standard
 * version and/or compiler.
 */


/**
 * C standard version, as a long integer in the format @em YYYYMM.
 *
 * If no standard is supported, its value is @c 0 instead.
 *
 * @code
 * #if (C_STANDARD >= 199901L)
 *     // Single line comment syntax is supported.
 * #endif
 * @endcode
 *
 * @hideinitializer
 */
#if (defined(__STDC__) && (__STDC__ + 0 != 0)) \
    || defined(_MSC_VER) \
    || defined(__cplusplus)
    /* C89 standard. */
#   define C_STANDARD 198900L
#elif defined(__STDC_VERSION__)
#   if __STDC_VERSION__ + 0 == 0
        /* C90 standard. */
#       define C_STANDARD 199000L
#   else
#       define C_STANDARD __STDC_VERSION__
#   endif
#else
    /* Pre-standard. */
#   define C_STANDARD 0
#endif


/**
 * Concatenates two text elements.
 *
 * @param [in] x first text element
 * @param [in] y second text element
 * @return single text element
 * @see #CONCATENATE_INDIRECT
 * @hideinitializer
 */
#if C_STANDARD
#   define CONCATENATE(x, y) x##y
#else
    /* Fix for Doxygen bug 601223. */
#   define CONCATENATE(x, y) x/* */y
#endif


/**
 * Concatenates two identifiers, after macro expansion.
 *
 * @param [in] x first identifier
 * @param [in] y second identifier
 * @return single text element
 * @see #CONCATENATE
 */
#define CONCATENATE_INDIRECT(x, y) \
    CONCATENATE(x, y)


/**
 * Disables copying of a C++ class or struct.
 *
 * @code
 * class Logger {
 *     DISABLE_TYPE_COPYING(Logger);
 *     
 * public:
 *     ...
 * };
 * @endcode
 *
 * @param [in] type data type name
 * @hideinitializer
 */
#if defined(__cplusplus) || defined(DOXYGEN)
#   define DISABLE_TYPE_COPYING(type) \
        private: \
            type(const type&); \
            void operator=(const type&)
#endif


/**
 * External C linkage attribute.
 *
 * @code
 * EXTERN_C void free(void* memory);
 * @endcode
 *
 * @see #PUBLIC
 * @hideinitializer
 */
#ifdef __cplusplus
#   define EXTERN_C extern "C"
#else
#   define EXTERN_C extern
#endif


/**
 * Name of the enclosing function, as a string.
 *
 * If this feature isn't available, the function name is @c "?" instead.
 *
 * @code
 * void example() {
 *     printf("Inside function \"%s\".\n", FUNCTION_NAME);
 * }
 * @endcode
 *
 * @hideinitializer
 */
#if defined(__GNUC__) || defined(_MSC_VER)
#   define FUNCTION_NAME __FUNCTION__
#elif (C_STANDARD >= 199901L) || defined(__cplusplus)
#   define FUNCTION_NAME __func__
#else
#   define FUNCTION_NAME "?"
#endif


/**
 * Inline function attribute.
 *
 * @code
 * INLINE bool strequal(const char* x, const char* y) {
 *     return strcmp(x, y) == 0;
 * }
 * @endcode
 *
 * @hideinitializer
 */
#if (C_STANDARD >= 199901L) || defined(__cplusplus)
#   define INLINE inline
#elif defined(__GNUC__)
#   define INLINE __inline__
#elif defined(_MSC_VER)
#   define INLINE __inline
#else
#   define INLINE
#endif


/**
 * Gets the length of an array, whose size must be known at compile time.
 *
 * @code
 * char buffer[256];
 * fgets(buffer, LENGTH_OF(buffer), stdin);
 * @endcode
 *
 * @param [in] array array for which to count the number of elements
 * @return number of elements in the array
 * @hideinitializer
 */
#ifdef _MSC_VER
#   ifdef __cplusplus
#       include <cstdlib>
#   else
#       include <stdlib.h>
#   endif
#endif

#if defined(_MSC_VER) && defined(_countof)
#   define LENGTH_OF _countof
#else
#   define LENGTH_OF(array) \
        (sizeof(array) / sizeof((array)[0]))
#endif


/**
 * Packed struct/union attribute.
 *
 * Indicates that each member should be placed such that the memory required is
 * the minimum possible (e.g. without any padding for alignment).
 *
 * If this feature isn't available, the attribute has no effect.
 *
 * @code
 * PACKED(struct GDT_Register {
 *     uint16_t size;
 *     uint32_t address;
 * });
 * 
 * STATIC_ASSERT(sizeof(GDT_Register) == 6, "GDT register not packed.");
 * @endcode
 *
 * @param [in] type struct or union definition to pack
 * @see #STATIC_ASSERT
 * @hideinitializer
 */
#if defined(__GNUC__)
#   define PACKED(type) \
        type __attribute__((__packed__))
#elif defined(_MSC_VER)
#   define PACKED(type) \
        PRAGMA(pack(push, 1)) type PRAGMA(pack(pop))
#else
#   define PACKED(type) type
#endif


/**
 * Declares a compiler pragma.
 *
 * @code
 * PRAGMA("options")
 * @endcode
 *
 * @param [in] directive string literal with the compiler directive
 * @hideinitializer
 */
#if (C_STANDARD >= 199901L) || defined(__cplusplus)
#   define PRAGMA _Pragma
#elif defined(_MSC_VER)
#   define PRAGMA __pragma
#else
#   define PRAGMA(directive)
#endif


/**
 * Global identifier attribute (implies @c #EXTERN_C).
 *
 * Allows to selectively export or import identifiers.
 *
 * @section exporting To export:
 * @code
 * #undef PUBLIC_API
 * #define PUBLIC_API PUBLIC_EXPORT
 * 
 * PUBLIC char* strcopy(const char* string);
 * @endcode
 *
 * @section importing To import:
 * @code
 * #undef PUBLIC_API
 * #define PUBLIC_API PUBLIC_IMPORT
 * 
 * PUBLIC char* strcopy(const char* string);
 * @endcode
 *
 * @see #EXTERN_C
 * @see #PUBLIC_EXPORT
 * @see #PUBLIC_IMPORT
 * @hideinitializer
 */
#define PUBLIC EXTERN_C PUBLIC_API

#ifndef PUBLIC_API
#   define PUBLIC_API
#endif


/**
 * Global exported identifier attribute.
 *
 * @warning This attribute shouldn't be used directly, only with @c #PUBLIC.
 * @hideinitializer
 */
#if defined(__CYGWIN__) || defined(__MINGW32__) || defined(_MSC_VER)
#   define PUBLIC_EXPORT __declspec(dllexport)
#else
#   define PUBLIC_EXPORT
#endif


/**
 * Global imported identifier attribute.
 *
 * @warning This attribute shouldn't be used directly, only with @c #PUBLIC.
 * @hideinitializer
 */
#if defined(__CYGWIN__) || defined(__MINGW32__) || defined(_MSC_VER)
#   define PUBLIC_IMPORT __declspec(dllimport)
#else
#   define PUBLIC_IMPORT
#endif


/**
 * Asserts that an expression is true, at compile time.
 *
 * @code
 * STATIC_ASSERT(sizeof(void*) == 4, "Not 32 bits.");
 * @endcode
 *
 * @param [in] expression expression to be tested at global scope
 * @param [in] message assertion failure message
 * @hideinitializer
 * @author Pádraig Brady
 * @see http://www.pixelbeat.org/programming/gcc/static_assert.html
 */
#define STATIC_ASSERT(expression, message) \
    enum {CONCATENATE_INDIRECT(STATIC_ASSERTION_, STATIC_ASSERT_ID) \
        = 1 / ((expression) ? 1 : 0)}

#ifdef _MSC_VER
#   define STATIC_ASSERT_ID __COUNTER__
#else
#   define STATIC_ASSERT_ID __LINE__
#endif


/**
 * Converts a text element to a string.
 *
 * @code
 * const char* year = TO_STRING(1986);
 * @endcode
 *
 * @param [in] text text element to convert
 * @return string representation of the given text element
 * @see #TO_STRING_INDIRECT
 * @hideinitializer
 */
#if C_STANDARD
#   define TO_STRING(text) #text
#else
#   define TO_STRING(text) "text"
#endif


/**
 * Converts an identifier to a string, after macro expansion.
 *
 * @code
 * const char* line = TO_STRING_INDIRECT(__LINE__);
 * @endcode
 *
 * @param [in] symbol identifier to convert
 * @return string representation of the given identifier
 * @see #TO_STRING
 */
#define TO_STRING_INDIRECT(symbol) \
    TO_STRING(symbol)


/**
 * Unused parameter attribute.
 *
 * @code
 * void example(UNUSED int p) {
 * }
 * @endcode
 *
 * @hideinitializer
 */
#ifdef __GNUC__
#   define UNUSED __attribute__((__unused__))
#else
#   define UNUSED
#endif


/**
 * Disables deprecation warnings.
 * 
 * @code
 * WARN_DEPRECATION_DISABLE
 * FILE* f = fopen("file", "r+");
 * @endcode
 *
 * @hideinitializer
 */
#ifdef _MSC_VER
#   define WARN_DEPRECATION_DISABLE \
        PRAGMA(warning(disable: 4996))
#else
#   define WARN_DEPRECATION_DISABLE
#endif


/**
 * Disables the warning given when a class has virtual functions and an
 * accessible non-virtual destructor, via a compiler pragma.
 * 
 * @code
 * class IReadable {
 *     WARN_NON_VIRTUAL_DTOR_DISABLE
 * 
 * public:
 *     virtual void read() = 0;
 * 
 * protected:
 *     ~IReadable() {}
 * };
 * @endcode
 *
 * @hideinitializer
 */
#if defined(__cplusplus) || defined(DOXYGEN)
#   if defined(__GNUC__) \
        && ((__GNUC__ > 4) \
            || ((__GNUC__ == 4) && (__GNUC_MINOR__ >= 2)))
        /* Can't use "-Wnon-virtual-dtor" if the following warning is in
           effect. */
#       define WARN_NON_VIRTUAL_DTOR_DISABLE \
            PRAGMA("GCC diagnostic ignored \"-Weffc++\"")
#   else
#       define WARN_NON_VIRTUAL_DTOR_DISABLE
#   endif
#endif


#endif
