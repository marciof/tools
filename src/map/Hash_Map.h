#ifndef SHOW__MAP__HASH_MAP_H
#define SHOW__MAP__HASH_MAP_H


#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Map.h"


enum Hash_Map_Properties {
    /**
     * Keys comparison function to use. If `NULL` uses the equals operator.
     */
    HASH_MAP_EQUAL,
    
    /**
     * Hash function to use. If `NULL` uses the key value.
     */
    HASH_MAP_HASH
};


/**
 * Keys comparison function.
 *
 * @param a first key
 * @param b second key
 * @return `true` if both keys are equal or `false` otherwise
 */
typedef bool (*Hash_Map_Equal)(intptr_t a, intptr_t b);


/**
 * Hash function.
 *
 * @param key key to hash
 * @return hash code for the given key
 */
typedef size_t (*Hash_Map_Hash)(intptr_t key);


/**
 * Hash table map implementation.
 *
 * The collision strategy used is a singly linked linear list.
 */
extern const Map_Impl Hash_Map;


/**
 * Compute a hash code using the One-at-a-Time algorithm.
 *
 * @param data data to hash
 * @param length data size, in bytes
 * @return hash code for the given data
 * @author Bob Jenkins
 * @see http://www.burtleburtle.net/bob/hash/doobs.html#one
 */
uint32_t Hash_Map_hash(uint8_t* data, size_t length);


/**
 * Compare two `NUL` terminated strings.
 *
 * @param a first string
 * @param b second string
 * @return `true` if both strings are equal or `false` otherwise
 */
bool Hash_Map_str_equal(intptr_t a, intptr_t b);


/**
 * Compute the hash code of a `NUL` terminated string.
 *
 * @param string string to hash
 * @return hash code for the given string
 */
size_t Hash_Map_str_hash(intptr_t string);


#endif
