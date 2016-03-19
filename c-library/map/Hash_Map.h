#ifndef __EON__LIBRARY__MAP__HASH_MAP__
#define __EON__LIBRARY__MAP__HASH_MAP__


/**
 * @file
 * @brief Hash map implementation
 *
 * Contains a hash map implementation using a map interface.
 */


#include "../types.h"
#include "../util.h"
#include "Map_Implementation.h"


/**
 * Valid properties for a hash map.
 *
 * @see #Map_get_property
 * @see #Map_set_property
 */
enum {
    /**
     * Keys comparison function to use. If @c #null uses the equals operator on
     * the @c #ptr_t::data component of a key.
     *
     * @note @b Type: @c #Hash_Map_Equals
     * @note @b Access: read/write
     */
    HASH_MAP_EQUALS,
    
    /**
     * Hash function to use. If @c #null uses the value of the @c #ptr_t::data
     * component of a key.
     *
     * @note @b Type: @c #Hash_Map_Hash
     * @note @b Access: read/write
     */
    HASH_MAP_HASH
};


/**
 * Keys comparison function.
 *
 * @param [in] x first key
 * @param [in] y second key
 * @return @c true if both keys are equal or @c false otherwise
 */
typedef bool (*Hash_Map_Equals)(ptr_t x, ptr_t y);


/**
 * Hash function.
 *
 * @param [in] key key to hash
 * @return hash code for the given key
 */
typedef size_t (*Hash_Map_Hash)(ptr_t key);


/**
 * Hash table map implementation.
 *
 * The collision strategy used is a singly linked linear list.
 *
 * @see #Map_new
 */
PUBLIC const Map_Implementation Hash_Map;


/**
 * Computes a hash code using the One-at-a-Time algorithm.
 *
 * @param [in] data data to hash
 * @param [in] length data size, in bytes
 * @return hash code for the given data
 * @author Bob Jenkins
 * @see http://www.burtleburtle.net/bob/hash/doobs.html#one
 */
PUBLIC uint32_t Hash_Map_hash(uint8_t* data, size_t length);


/**
 * Compares two @c NULL terminated strings.
 *
 * @param [in] x first string
 * @param [in] y second string
 * @return @c true if both strings are equal or @c false otherwise
 * @see #Hash_Map_stringz_hash
 */
PUBLIC bool Hash_Map_stringz_equals(ptr_t x, ptr_t y);


/**
 * Computes the hash code of a @c NULL terminated string.
 *
 * @param [in] string string to hash
 * @return hash code for the given string
 * @see #Hash_Map_stringz_equals
 */
PUBLIC size_t Hash_Map_stringz_hash(ptr_t string);


#endif
