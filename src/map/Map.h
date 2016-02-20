#ifndef SHOW__MAP__MAP_H
#define SHOW__MAP__MAP_H


#include <stddef.h>
#include <stdint.h>
#include "../iterator/Iterator.h"
#include "../list/List.h"
#include "../std/Error.h"


typedef struct _Map* Map;

typedef struct _Map_Impl {
    Iterator_Impl keys_iterator;
    void* (*create)(Error* error);
    void (*destroy)(void* map, Error* error);
    intptr_t (*get)(void* map, intptr_t key, Error* error);
    intptr_t (*get_property)(void* map, size_t property, Error* error);
    intptr_t (*put)(void* map, intptr_t key, intptr_t value, Error* error);
    intptr_t (*remove)(void* map, intptr_t key, Error* error);
    void (*set_property)(
        void* map, size_t property, intptr_t value, Error* error);
    size_t (*size)(void* map);
}* Map_Impl;


/**
 * Delete a map.
 *
 * @param map map to delete, unless `NULL`
 * @param error error message, if any
 * @exception EPERM map is being iterated
 */
void Map_delete(Map map, Error* error);


/**
 * Get the value of a key in a map.
 *
 * @param map map from which to retrieve the value
 * @param key key whose associated value is to be retrieved
 * @param error error message, if any
 * @return associated value or `NULL` on error
 * @exception EINVAL unknown key
 */
intptr_t Map_get(Map map, intptr_t key, Error* error);


/**
 * Query the value of a map property.
 *
 * @param map map for which to query a property
 * @param property property to query
 * @param error error message, if any
 * @return property's value or `NULL` on error
 * @exception EINVAL unknown property
 */
intptr_t Map_get_property(Map map, size_t property, Error* error);


/**
 * Check if a key exists in a map.
 *
 * @param map map in which to check
 * @param key key whose association is to be checked
 * @return `true` if the key exists or `false` otherwise
 */
bool Map_has_key(Map map, intptr_t key);


/**
 * Get all keys from a map.
 *
 * @param map map from which to retrieve all keys
 * @param error error message, if any
 * @return new list with all keys in the map or `NULL` on error
 * @exception ENOMEM not enough memory
 */
List Map_keys(Map map, Error* error);


/**
 * Create an iterator for a map's keys.
 *
 * @param map map for which to create an iterator
 * @param error error message, if any
 * @return new iterator for the given map or `NULL` on error
 * @exception ENOMEM not enough memory
 * @exception EPERM maximum number of iterators (`SIZE_MAX`) reached
 */
Iterator Map_keys_iterator(Map map, Error* error);


/**
 * Associate a value with a key in a map.
 *
 * @param map map in which to create the association
 * @param key key with which to associate the value
 * @param value value to be associated with the key
 * @param error error message, if any
 * @return previously associated value or `NULL` if it didn't exist before or
 *         on error
 * @exception ENOMEM not enough memory
 * @exception EPERM map is being iterated
 * @exception EPERM maximum number of elements (`SIZE_MAX`) reached
 */
intptr_t Map_put(Map map, intptr_t key, intptr_t value, Error* error);


/**
 * Create a map.
 *
 * @param implementation map implementation to use
 * @param error error message, if any
 * @return new empty map or `NULL` on error
 * @exception ENOMEM not enough memory
 */
Map Map_new(Map_Impl implementation, Error* error);


/**
 * Remove the association of a value with a key in a map.
 *
 * @param map map in which to remove the association
 * @param key key whose association is to be removed
 * @param error error message, if any
 * @return associated value or `NULL` on error
 * @exception EINVAL unknown key
 * @exception ENOMEM not enough memory
 * @exception EPERM map is being iterated
 */
intptr_t Map_remove(Map map, intptr_t key, Error* error);


/**
 * Define the value of a map property.
 *
 * @param map map for which to define a property
 * @param property property to define
 * @param value property's value
 * @param error error message, if any
 * @return `true` if the property was correctly set or `false` otherwise
 * @exception EINVAL unknown property or invalid value
 */
bool Map_set_property(Map map, size_t property, intptr_t value, Error* error);


/**
 * Get the size of a map.
 *
 * @param map map for which to count the number of associations
 * @return number of key/value associations in the map
 */
size_t Map_size(Map map);


/**
 * Get all values from a map.
 *
 * @param map map from which to retrieve all values
 * @param error error message, if any
 * @return new list with all values in the map or `NULL` on error
 * @exception ENOMEM not enough memory
 */
List Map_values(Map map, Error* error);


#endif
