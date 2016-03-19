#ifndef __EON__LIBRARY__MAP__MAP__
#define __EON__LIBRARY__MAP__MAP__


/**
 * @file
 * @brief Map interface
 *
 * Defines the interface to manipulate map instances.
 */


#include "../iterator/Iterator.h"
#include "../list/List.h"
#include "../util.h"
#include "Map_Implementation.h"


/**
 * Map instance.
 */
typedef struct _Map* Map;


/**
 * Deletes a map.
 *
 * @param [in,out] map map to delete, @c unless NULL
 * @see #Map_new
 * @note Errors that set @c errno to:
 *       - @c EPERM: Map is being iterated.
 */
PUBLIC void Map_delete(Map map);


/**
 * Gets the value of a key in a map.
 *
 * @param [in] map map from which to retrieve the value
 * @param [in] key key whose associated value is to be retrieved
 * @return associated value or @c #null on error (see note)
 * @see #Map_has_key
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Unknown key.
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC ptr_t Map_get(Map map, ptr_t key);


/**
 * Queries the value of a map property.
 *
 * @param [in] map map for which to query a property
 * @param [in] property property to query
 * @return property's value or @c #null on error (see note)
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Unknown property.
 */
PUBLIC ptr_t Map_get_property(Map map, size_t property);


/**
 * Checks if a key exists in a map.
 *
 * @param [in] map map in which to check
 * @param [in] key key whose association is to be checked
 * @return @c true if the key exists or @c false otherwise or on error (see
 *         note)
 * @see #Map_get
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC bool Map_has_key(Map map, ptr_t key);


/**
 * Gets all keys from a map.
 *
 * @param [in] map map from which to retrieve all keys
 * @return new list with all keys in the map or @c NULL on error (see note)
 * @see #Map_values
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC List Map_keys(Map map);


/**
 * Creates an iterator for a map's keys.
 *
 * @code
 * Iterator i = Map_keys_iterator(m);
 * 
 * while (Iterator_has_next(i)) {
 *     ptr_t key = Iterator_next(i);
 *     ...
 * }
 * 
 * Iterator_delete(i);
 * @endcode
 *
 * @param [in] map map for which to create an iterator
 * @return new iterator for the given map or @c NULL on error (see note)
 * @see #Iterator_delete
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 *       - @c EPERM: Maximum number of iterators (@c SIZE_MAX) reached.
 */
PUBLIC Iterator Map_keys_iterator(Map map);


/**
 * Associates a value with a key in a map.
 *
 * @param [in,out] map map in which to create the association
 * @param [in] key key with which to associate the value
 * @param [in] value value to be associated with the key
 * @return previously associated value or @c #null if it didn't exist before or
 *         on error (see note)
 * @see #Map_remove
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 *       - @c EPERM: Map is being iterated.
 *       - @c EPERM: Maximum number of elements (@c SIZE_MAX) reached.
 */
PUBLIC ptr_t Map_put(Map map, ptr_t key, ptr_t value);


/**
 * Creates a map.
 *
 * @code
 * Map m = Map_new(Hash_Map);
 * ...
 * Map_delete(m);
 * @endcode
 *
 * @param [in] implementation map implementation to use
 * @return new empty map or @c NULL on error (see note)
 * @see #Map_delete
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC Map Map_new(Map_Implementation implementation);


/**
 * Removes the association of a value with a key in a map.
 *
 * @param [in,out] map map in which to remove the association
 * @param [in] key key whose association is to be removed
 * @return associated value or @c #null on error (see note)
 * @see #Map_put
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Unknown key.
 *       - @c ENOMEM: Not enough memory.
 *       - @c EPERM: Map is being iterated.
 */
PUBLIC ptr_t Map_remove(Map map, ptr_t key);


/**
 * Defines the value of a map property.
 *
 * @param [in,out] map map for which to define a property
 * @param [in] property property to define
 * @param [in] value property's value
 * @return @c true if the property was correctly set or @c false otherwise
 * @note Errors that set @c errno to:
 *       - @c EINVAL: Unknown property or invalid value.
 */
PUBLIC bool Map_set_property(Map map, size_t property, ptr_t value);


/**
 * Gets the size of a map.
 *
 * @param [in] map map for which to count the number of associations
 * @return number of key/value associations in the map
 */
PUBLIC size_t Map_size(Map map);


/**
 * Gets all values from a map.
 *
 * @param [in] map map from which to retrieve all values
 * @return new list with all values in the map or @c NULL on error (see note)
 * @see #Map_keys
 * @note Errors that set @c errno to:
 *       - @c ENOMEM: Not enough memory.
 */
PUBLIC List Map_values(Map map);


#endif
