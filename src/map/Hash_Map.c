#include <assert.h>
#include <errno.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/types.h>
#include "Hash_Map.h"


#define DEFAULT_INITIAL_CAPACITY ((size_t) 16)
#define DEFAULT_LOAD_FACTOR ((float) 0.75)


enum Hash_Iterator_Direction {
    BACKWARD, FORWARD
};

enum Hash_Iterator_Location {
    END, MIDDLE, START
};


typedef struct _Hash_Bucket {
    struct _Hash_Bucket* next;
    intptr_t key;
    intptr_t value;
}* Hash_Bucket;


typedef struct _Hash {
    bool (*equals)(intptr_t x, intptr_t y);
    size_t (*hash)(intptr_t key);
    
    // Number of buckets (must be a power of 2).
    size_t capacity;
    
    size_t size;
    size_t iterators;
    Hash_Bucket* table;
    
    // Indicates how full the table can get before its capacity is
    // automatically increased. This is a percentage [0, 1] which measures
    // the maximum size the table can have. When the number of key/value
    // associations exceeds "load factor * capacity", the table size is doubled.
    float load_factor;
}* Hash;


typedef struct _Hash_Iterator_Position {
    size_t bucket;
    Hash_Bucket element;
}* Hash_Iterator_Position;


typedef struct _Hash_Iterator {
    Hash map;
    struct _Hash_Iterator_Position position;
    unsigned int direction : 1;
    unsigned int location : 2;
}* Hash_Iterator;


/**
 * Get the bucket of a key in a hash map.
 *
 * @param map hash map from which to retrieve the bucket
 * @param key key whose associated bucket is to be retrieved
 * @return associated bucket
 */
static Hash_Bucket* bucket_of(Hash map, intptr_t key) {
    size_t bit_mask = map->capacity - 1;
    return &map->table[map->hash(key) & bit_mask];
}


/**
 * Default keys comparison function.
 *
 * @param a first key
 * @param b second key
 * @return `true` if both keys are equal or `false` otherwise
 */
static bool default_equals(intptr_t a, intptr_t b) {
    return a == b;
}


/**
 * Default hash function.
 *
 * @param key key to hash
 * @return key itself as the hash code
 */
static size_t default_hash(intptr_t key) {
    return (size_t) key;
}


/**
 * Delete the given hash map table.
 *
 * @param table hash map table to delete
 * @param capacity hash map capacity
 */
static void delete_table(Hash_Bucket* table, size_t capacity) {
    for (size_t i = 0; i < capacity; ++i) {
        Hash_Bucket element = table[i];
        
        while (element != NULL) {
            Hash_Bucket next = element->next;
            memset(element, 0, sizeof(struct _Hash_Bucket));
            free(element);
            element = next;
        }
    }

    memset(table, 0, sizeof(Hash_Bucket) * capacity);
    free(table);
}


/**
 * Double the capacity of a hash map.
 *
 * @param map hash map whose capacity is to be doubled
 * @return `true` if the capacity was doubled or `false` otherwise
 */
static bool double_capacity(Hash map) {
    const size_t OLD_CAPACITY = map->capacity;
    Hash_Bucket* const OLD_TABLE = map->table;
    size_t i;
    
    map->capacity = 2 * OLD_CAPACITY;
    
    // Set all buckets to NULL.
    map->table = (Hash_Bucket*)
        calloc(map->capacity, sizeof(Hash_Bucket));
    
    if (map->table == NULL) {
        map->capacity = OLD_CAPACITY;
        map->table = OLD_TABLE;
        
        return false;
    }
    
    // Update old buckets to new ones.
    for (i = 0; i < OLD_CAPACITY; ++i) {
        Hash_Bucket e;
        
        for (e = OLD_TABLE[i]; e != NULL; e = e->next) {
            Hash_Bucket* bucket = bucket_of(map, e->key);
            Hash_Bucket f = (Hash_Bucket)
                malloc(sizeof(struct _Hash_Bucket));
            
            if (f != NULL) {
                f->next = *bucket;
                f->key = e->key;
                f->value = e->value;
                
                *bucket = f;
            }
            else {
                // Rollback.
                for (i = 0; i < map->capacity; ++i) {
                    for (f = map->table[i]; f != NULL; ) {
                        Hash_Bucket next = f->next;
                        free(f);
                        f = next;
                    }
                }
                
                free(map->table);
                
                map->capacity = OLD_CAPACITY;
                map->table = OLD_TABLE;
                
                return false;
            }
        }
    }
    
    delete_table(OLD_TABLE, OLD_CAPACITY);
    return true;
}


/**
 * Get the next position for a hash map.
 *
 * @param position current position
 * @param next where to store the next position
 * @param map hash map for which to get the next position
 * @return `true` if there is one or `false` otherwise
 */
static bool get_next(
        struct _Hash_Iterator_Position position,
        Hash_Iterator_Position next,
        Hash map) {

    if (position.element == NULL) {
        while (map->table[position.bucket] == NULL) {
            ++position.bucket;
        }
        
        if (next != NULL) {
            next->bucket = position.bucket;
            next->element = map->table[position.bucket];
        }
        
        return true;
    }
    else if (position.element->next == NULL) {
        size_t bucket = position.bucket;
        
        do {
            ++bucket;
        }
        while ((bucket < map->capacity) && (map->table[bucket] == NULL));
        
        if (bucket >= map->capacity) {
            return false;
        }
        
        position.bucket = bucket;
        position.element = NULL;
        
        return get_next(position, next, map);
    }
    else {
        if (next != NULL) {
            next->element = position.element->next;
        }
        
        return true;
    }
}


/**
 * Get the previous position for a hash map.
 *
 * @param position current position
 * @param previous where to store the previous position
 * @param map hash map for which to get the previous position
 * @return `true` if there is one or `false` otherwise
 */
static bool get_previous(
        struct _Hash_Iterator_Position position,
        Hash_Iterator_Position previous,
        Hash map){

    if (position.element == NULL) {
        while (map->table[position.bucket] == NULL) {
            --position.bucket;
        }
        
        position.element = map->table[position.bucket];
        
        while (position.element->next != NULL) {
            position.element = position.element->next;
        }
        
        if (previous != NULL) {
            *previous = position;
        }
        
        return true;
    }
    else if (position.element == map->table[position.bucket]) {
        ssize_t bucket = position.bucket;
        
        do {
            --bucket;
        }
        while ((bucket >= 0) && (map->table[bucket] == NULL));
        
        if (bucket < 0) {
            return false;
        }
        
        position.bucket = (size_t) bucket;
        position.element = NULL;
        
        return get_previous(position, previous, map);
    }
    else {
        Hash_Bucket element = map->table[position.bucket];
        
        while (element->next != position.element) {
            element = element->next;
        }
        
        if (previous != NULL) {
            previous->bucket = position.bucket;
            previous->element = element;
        }
        
        return true;
    }
}


/**
 * Initialize a hash map, if needed.
 *
 * @param map hash map to initialize
 * @param error error message, if any
 */
static void initialize(Hash map, Error* error) {
    if (map->table != NULL) {
        Error_clear(error);
        return;
    }

    double power = log((double) map->capacity) / log((double) 2);
    assert(power == ceil(power));
    assert(map->load_factor >= 0);
    assert(map->load_factor <= 1);
    
    // calloc is used to set all buckets to NULL.
    Hash_Bucket* table = (Hash_Bucket*) calloc(
        map->capacity, sizeof(Hash_Bucket));
    
    if (table == NULL) {
        Error_set(error, strerror(ENOMEM));
        return;
    }
    
    map->table = table;
    Error_clear(error);
    return;
}


/**
 * Associate a value with a key in a hash map.
 *
 * @param map hash map in which to create the association
 * @param key key with which to associate the value
 * @param value value to be associated with the key
 * @param error error message, if any
 * @return previously associated value or `NULL` if it didn't exist before or
 *         on error
 */
static intptr_t put_key(Hash map, intptr_t key, intptr_t value, Error* error) {
    Hash_Bucket* bucket = bucket_of(map, key);
    Hash_Bucket e;
    
    for (e = *bucket; e != NULL; e = e->next) {
        if (map->equals(e->key, key)) {
            intptr_t previous_value = e->value;
            e->value = value;
            
            Error_clear(error);
            return previous_value;
        }
    }
    
    e = (Hash_Bucket) malloc(sizeof(struct _Hash_Bucket));
    
    if (e == NULL) {
        Error_set(error, strerror(ENOMEM));
        return 0;
    }
    
    e->next = *bucket;
    e->key = key;
    e->value = value;
    
    *bucket = e;
    ++map->size;
    
    Error_clear(error);
    return 0;
}


/**
 * Remove the association of a value with a key in a hash map.
 *
 * @param map hash map in which to remove the association
 * @param key key whose association is to be removed
 * @param error error message, if any
 * @return associated value or `NULL` on error
 */
static intptr_t remove_key(Hash map, intptr_t key, Error* error) {
    Hash_Bucket* bucket = bucket_of(map, key);
    Hash_Bucket e, previous = NULL;
    
    for (e = *bucket; e != NULL; previous = e, e = e->next) {
        if (map->equals(e->key, key)) {
            intptr_t value = e->value;
            
            if (previous == NULL) {
                *bucket = e->next;
            }
            else {
                previous->next = e->next;
            }
            
            free(e);
            --map->size;
            
            Error_clear(error);
            return value;
        }
    }
    
    Error_set(error, strerror(EINVAL));
    return 0;
}


static void* create(Error* error) {
    Hash map = (Hash) malloc(sizeof(struct _Hash));
    
    if (map == NULL) {
        Error_set(error, strerror(ENOMEM));
        return NULL;
    }
    
    map->equals = default_equals;
    map->hash = default_hash;
    map->capacity = DEFAULT_INITIAL_CAPACITY;
    map->size = 0;
    map->iterators = 0;
    map->table = NULL;
    map->load_factor = DEFAULT_LOAD_FACTOR;
    
    Error_clear(error);
    return map;
}


static void destroy(void* m, Error* error) {
    Hash map = (Hash) m;
    
    if (map->iterators > 0) {
        Error_set(error, strerror(EPERM));
        return;
    }

    if (map->table != NULL) {
        delete_table(map->table, map->capacity);
    }

    memset(map, 0, sizeof(struct _Hash));
    free(map);
    Error_clear(error);
}


static intptr_t get(void* m, intptr_t key, Error* error) {
    Hash map = (Hash) m;

    if (map->table == NULL) {
        Error_set(error, strerror(EINVAL));
        return 0;
    }

    for (Hash_Bucket e = *bucket_of(map, key); e != NULL; e = e->next) {
        if (map->equals(e->key, key)) {
            Error_clear(error);
            return e->value;
        }
    }
    
    Error_set(error, strerror(EINVAL));
    return 0;
}


static intptr_t get_property(void* m, size_t property, Error* error) {
    Hash map = (Hash) m;
    
    switch (property) {
    case HASH_MAP_EQUAL:
        Error_clear(error);
        return (intptr_t) (map->equals == default_equals ? NULL : map->equals);
    case HASH_MAP_HASH:
        Error_clear(error);
        return (intptr_t) (map->hash == default_hash ? NULL : map->hash);
    default:
        Error_set(error, strerror(EINVAL));
        return 0;
    }
}


static intptr_t put(void* m, intptr_t key, intptr_t value, Error* error) {
    Hash map = (Hash) m;
    
    if ((map->size == SIZE_MAX) || (map->iterators > 0)) {
        Error_set(error, strerror(EPERM));
        return 0;
    }

    initialize(map, error);

    if (Error_has(error)) {
        return 0;
    }

    if (map->size >= (size_t) (map->load_factor * map->capacity)) {
        // Expand the table, if it fails try again next time.
        double_capacity(map);
    }
    
    return put_key(map, key, value, error);
}


static intptr_t remove(void* m, intptr_t key, Error* error) {
    Hash map = (Hash) m;
    
    if (map->iterators > 0) {
        Error_set(error, strerror(EPERM));
        return 0;
    }

    initialize(map, error);

    if (Error_has(error)) {
        return 0;
    }
    
    return remove_key(map, key, error);
}


static void set_property(
        void* m, size_t property, intptr_t value, Error* error) {

    Hash map = (Hash) m;
    
    switch (property) {
    case HASH_MAP_EQUAL:
        map->equals = value ? (Hash_Map_Equal) value : default_equals;
        Error_clear(error);
        break;
    case HASH_MAP_HASH:
        map->hash = value ? (Hash_Map_Hash) value : default_hash;
        Error_clear(error);
        break;
    default:
        Error_set(error, strerror(EINVAL));
        break;
    }
}


static size_t size(void* m) {
    return ((Hash) m)->size;
}


static void* create_for_string_keys(Error* error) {
    Hash map = (Hash) create(error);

    if (Error_has(error)) {
        return NULL;
    }

    set_property(map, HASH_MAP_EQUAL, (intptr_t) Hash_Map_str_equal, NULL);
    set_property(map, HASH_MAP_HASH, (intptr_t) Hash_Map_str_hash, NULL);

    return map;
}


static void iterator_to_end(void* it) {
    Hash_Iterator iterator = (Hash_Iterator) it;
    
    iterator->position.bucket = iterator->map->capacity - 1;
    iterator->position.element = NULL;
    iterator->direction = BACKWARD;
    iterator->location = END;
}


static void iterator_to_start(void* it) {
    Hash_Iterator iterator = (Hash_Iterator) it;
    
    iterator->position.bucket = 0;
    iterator->position.element = NULL;
    iterator->direction = FORWARD;
    iterator->location = START;
}


static void* iterator_create(void* collection, Error* error) {
    Hash map = (Hash) collection;

    if (map->iterators == SIZE_MAX) {
        Error_set(error, strerror(EPERM));
        return NULL;
    }
    
    Hash_Iterator iterator = (Hash_Iterator) malloc(
        sizeof(struct _Hash_Iterator));
    
    if (iterator == NULL) {
        Error_set(error, strerror(ENOMEM));
        return NULL;
    }
    
    iterator->map = map;
    ++map->iterators;

    iterator_to_start(iterator);
    Error_clear(error);
    return iterator;
}


static void iterator_destroy(void* it) {
    --((Hash_Iterator) it)->map->iterators;
    memset(it, 0, sizeof(struct _Hash_Iterator));
    free(it);
}


static bool iterator_has_next(void* it) {
    Hash_Iterator iterator = (Hash_Iterator) it;
    return (iterator->map->size > 0) && (iterator->location != END);
}


static bool iterator_has_previous(void* it) {
    Hash_Iterator iterator = (Hash_Iterator) it;
    return (iterator->map->size > 0) && (iterator->location != START);
}


static intptr_t iterator_next(void* it, Error* error) {
    Hash_Iterator iterator = (Hash_Iterator) it;

    if (!iterator_has_next(iterator)) {
        Error_set(error, strerror(EPERM));
        return 0;
    }
    
    if (iterator->location == START) {
        get_next(iterator->position, &iterator->position, iterator->map);
        iterator->direction = FORWARD;
        iterator->location = MIDDLE;
    }
    else if (iterator->direction == BACKWARD) {
        iterator->direction = FORWARD;
    }
    else {
        get_next(iterator->position, &iterator->position, iterator->map);
    }
    
    intptr_t key = iterator->position.element->key;
    
    if (!get_next(iterator->position, NULL, iterator->map)) {
        iterator_to_end(iterator);
    }
    
    Error_clear(error);
    return key;
}


static intptr_t iterator_previous(void* it, Error* error) {
    Hash_Iterator iterator = (Hash_Iterator) it;

    if (!iterator_has_previous(iterator)) {
        Error_set(error, strerror(EPERM));
        return 0;
    }
    
    if (iterator->location == END) {
        get_previous(iterator->position, &iterator->position, iterator->map);
        iterator->direction = BACKWARD;
        iterator->location = MIDDLE;
    }
    else if (iterator->direction == FORWARD) {
        iterator->direction = BACKWARD;
    }
    else {
        get_previous(iterator->position, &iterator->position, iterator->map);
    }
    
    intptr_t key = iterator->position.element->key;
    
    if (!get_previous(iterator->position, NULL, iterator->map)) {
        iterator_to_start(iterator);
    }
    
    Error_clear(error);
    return key;
}


static const struct _Iterator_Impl keys_iterator_impl = {
    iterator_create,
    iterator_destroy,
    iterator_to_end,
    iterator_to_start,
    iterator_has_next,
    iterator_has_previous,
    iterator_next,
    iterator_previous
};


static const struct _Map_Impl impl = {
    (Iterator_Impl) &keys_iterator_impl,
    create,
    destroy,
    get,
    get_property,
    put,
    remove,
    set_property,
    size
};


static const struct _Map_Impl string_impl = {
    (Iterator_Impl) &keys_iterator_impl,
    create_for_string_keys,
    destroy,
    get,
    get_property,
    put,
    remove,
    set_property,
    size
};


const Map_Impl Hash_Map = (Map_Impl) &impl;
const Map_Impl String_Hash_Map = (Map_Impl) &string_impl;


uint32_t Hash_Map_hash(uint8_t* data, size_t length) {
    uint32_t hash_code = 0;
    size_t i;
    
    for (i = 0; i < length; ++i) {
        hash_code += data[i];
        hash_code += (hash_code << 10);
        hash_code ^= (hash_code >> 6);
    }
    
    hash_code += (hash_code << 3);
    hash_code ^= (hash_code >> 11);
    hash_code += (hash_code << 15);
    
    return hash_code;
}


bool Hash_Map_str_equal(intptr_t a, intptr_t y) {
    return strcmp((char*) a, (char*) y) == 0;
}


size_t Hash_Map_str_hash(intptr_t key) {
    size_t length = strlen((char*) key) * sizeof(char);
    return Hash_Map_hash((uint8_t*) key, length);
}
