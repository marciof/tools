#include <assert.h>

#include "../std/math.h"
#include "../std/stdlib.h"
#include "../std/string.h"
#include "Hash_Map.h"


#define DEFAULT_INITIAL_CAPACITY ((size_t) 16)
#define DEFAULT_LOAD_FACTOR ((float) 0.75)


enum Iterator_Direction {
    BACKWARD, FORWARD
};

enum Iterator_Location {
    END, MIDDLE, START
};


typedef struct _Bucket_Element* Bucket_Element;

struct _Bucket_Element {
    Bucket_Element next;
    ptr_t key;
    ptr_t value;
};


typedef struct _Map* Map;

struct _Map {
    bool (*equals)(ptr_t x, ptr_t y);
    size_t (*hash)(ptr_t key);
    
    /* Number of buckets (must be a power of 2). */
    size_t capacity;
    
    size_t size;
    size_t iterators;
    Bucket_Element* table;
    
    /* Indicates how full the table can get before its capacity is automatically
       increased. This is a percentage [0, 1] which measures the maximum size
       the table can have. When the number of key/value associations exceeds
       "load factor * capacity", the table size is doubled. */
    float load_factor;
};


typedef struct _Position* Position;

struct _Position {
    size_t bucket;
    Bucket_Element element;
};


typedef struct _Iterator* Iterator;

struct _Iterator {
    Map map;
    struct _Position position;
    unsigned int direction : 1;
    unsigned int location : 2;
};


/**
 * Gets the bucket of a key in a hash map.
 *
 * @param [in] map hash map from which to retrieve the bucket
 * @param [in] key key whose associated bucket is to be retrieved
 * @return associated bucket
 */
static INLINE Bucket_Element* bucket_of(Map map, ptr_t key) {
    size_t bit_mask = map->capacity - 1;
    return &map->table[map->hash(key) & bit_mask];
}


/**
 * Default keys comparison function.
 *
 * @param [in] x first key
 * @param [in] y second key
 * @return @c true if both keys are equal or @c false otherwise
 * @see #default_hash
 */
static bool default_equals(ptr_t x, ptr_t y) {
    return x.data == y.data;
}


/**
 * Default hash function.
 *
 * @param [in] key key to hash
 * @return key itself as the hash code
 * @see #default_equals
 */
static size_t default_hash(ptr_t key) {
    return (size_t) key.data;
}


/**
 * Deletes the given hash map table.
 *
 * @param [in,out] table hash map table to delete
 * @param [in] capacity hash map capacity
 */
static void delete_table(Bucket_Element* table, size_t capacity) {
    size_t i;
    
    for (i = 0; i < capacity; ++i) {
        Bucket_Element element = table[i];
        
        while (element != NULL) {
            Bucket_Element next = element->next;
            
            memset(element, 0, sizeof(struct _Bucket_Element));
            free(element);
            
            element = next;
        }
    }

    memset(table, 0, sizeof(Bucket_Element) * capacity);
    free(table);
}


/**
 * Doubles the capacity of a hash map.
 *
 * @param [in,out] map hash map whose capacity is to be doubled
 * @return @c ENONE if the capacity was doubled or an error code otherwise
 */
static int double_capacity(Map map) {
    const size_t OLD_CAPACITY = map->capacity;
    Bucket_Element* const OLD_TABLE = map->table;
    size_t i;
    
    map->capacity = 2 * OLD_CAPACITY;
    
    /* Set all buckets to NULL. */
    map->table = (Bucket_Element*)
        calloc(map->capacity, sizeof(Bucket_Element));
    
    if (map->table == NULL) {
        map->capacity = OLD_CAPACITY;
        map->table = OLD_TABLE;
        
        return ENOMEM;
    }
    
    /* Update old buckets to new ones. */
    for (i = 0; i < OLD_CAPACITY; ++i) {
        Bucket_Element e;
        
        for (e = OLD_TABLE[i]; e != NULL; e = e->next) {
            Bucket_Element* bucket = bucket_of(map, e->key);
            Bucket_Element f = (Bucket_Element)
                malloc(sizeof(struct _Bucket_Element));
            
            if (f != NULL) {
                f->next = *bucket;
                f->key = e->key;
                f->value = e->value;
                
                *bucket = f;
            }
            else {
                /* Rollback. */
                for (i = 0; i < map->capacity; ++i) {
                    for (f = map->table[i]; f != NULL; ) {
                        Bucket_Element next = f->next;
                        free(f);
                        f = next;
                    }
                }
                
                free(map->table);
                
                map->capacity = OLD_CAPACITY;
                map->table = OLD_TABLE;
                
                return ENOMEM;
            }
        }
    }
    
    delete_table(OLD_TABLE, OLD_CAPACITY);
    return ENONE;
}


/**
 * Gets the next position for a hash map.
 *
 * @param [in] position current position
 * @param [in,out] next where to store the next position
 * @param [in] map hash map for which to get the next position
 * @return @c true if there is one or @c false otherwise
 * @see #get_previous
 */
static bool get_next(struct _Position position, Position next, Map map) {
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
 * Gets the previous position for a hash map.
 *
 * @param [in] position current position
 * @param [in,out] previous where to store the previous position
 * @param [in] map hash map for which to get the previous position
 * @return @c true if there is one or @c false otherwise
 * @see #get_next
 */
static bool get_previous(struct _Position position, Position previous, Map map){
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
        
        position.bucket = bucket;
        position.element = NULL;
        
        return get_previous(position, previous, map);
    }
    else {
        Bucket_Element element = map->table[position.bucket];
        
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
 * Initializes a hash map, if needed.
 *
 * @param [out] error location where to store the error code
 * @param [in,out] map hash map to initialize
 * @return error code for this operation
 */
static int initialize(int* error, Map map) {
    Bucket_Element* table;
    double power;
    
    if (map->table != NULL) {
        *error = ENONE;
        return *error;
    }
    
    power = log((double) map->capacity) / log((double) 2);
    assert(power == ceil(power));
    assert(map->load_factor >= 0);
    assert(map->load_factor <= 1);
    
    /* calloc is used to set all buckets to NULL. */
    table = (Bucket_Element*) calloc(map->capacity, sizeof(Bucket_Element));
    
    if (table == NULL) {
        *error = ENOMEM;
        return *error;
    }
    
    map->table = table;
    *error = ENONE;
    return *error;
}


/**
 * Associates a value with a key in a hash map.
 *
 * @param [out] error location where to store the error code
 * @param [in,out] map hash map in which to create the association
 * @param [in] key key with which to associate the value
 * @param [in] value value to be associated with the key
 * @return previously associated value or @c NULL if it didn't exist before or
 *         on error
 * @see #remove_key
 */
static ptr_t put_key(int* error, Map map, ptr_t key, ptr_t value) {
    Bucket_Element* bucket = bucket_of(map, key);
    Bucket_Element e;
    
    for (e = *bucket; e != NULL; e = e->next) {
        if (map->equals(e->key, key)) {
            ptr_t previous_value = e->value;
            e->value = value;
            
            *error = ENONE;
            return previous_value;
        }
    }
    
    e = (Bucket_Element) malloc(sizeof(struct _Bucket_Element));
    
    if (e == NULL) {
        *error = ENOMEM;
        return null;
    }
    
    e->next = *bucket;
    e->key = key;
    e->value = value;
    
    *bucket = e;
    ++map->size;
    
    *error = ENONE;
    return null;
}


/**
 * Removes the association of a value with a key in a hash map.
 *
 * @param [out] error location where to store the error code
 * @param [in,out] map hash map in which to remove the association
 * @param [in] key key whose association is to be removed
 * @return associated value or @c NULL on error
 * @see #put_key
 */
static ptr_t remove_key(int* error, Map map, ptr_t key) {
    Bucket_Element* bucket = bucket_of(map, key);
    Bucket_Element e, previous = NULL;
    
    for (e = *bucket; e != NULL; previous = e, e = e->next) {
        if (map->equals(e->key, key)) {
            ptr_t value = e->value;
            
            if (previous == NULL) {
                *bucket = e->next;
            }
            else {
                previous->next = e->next;
            }
            
            free(e);
            --map->size;
            
            *error = ENONE;
            return value;
        }
    }
    
    *error = EINVAL;
    return null;
}


static void* create(int* error) {
    Map map = (Map) malloc(sizeof(struct _Map));
    
    if (map == NULL) {
        *error = ENOMEM;
        return NULL;
    }
    
    map->equals = default_equals;
    map->hash = default_hash;
    map->capacity = DEFAULT_INITIAL_CAPACITY;
    map->size = 0;
    map->iterators = 0;
    map->table = NULL;
    map->load_factor = DEFAULT_LOAD_FACTOR;
    
    *error = ENONE;
    return map;
}


static void destroy(int* error, void* m) {
    Map map = (Map) m;
    
    if (map->iterators > 0) {
        *error = EPERM;
    }
    else {
        if (map->table != NULL) {
            delete_table(map->table, map->capacity);
        }
        
        memset(map, 0, sizeof(struct _Map));
        free(map);
        
        *error = ENONE;
    }
}


static ptr_t get(int* error, void* m, ptr_t key) {
    Map map = (Map) m;
    Bucket_Element e;
    
    if (initialize(error, map) != ENONE) {
        return null;
    }
    
    for (e = *bucket_of(map, key); e != NULL; e = e->next) {
        if (map->equals(e->key, key)) {
            *error = ENONE;
            return e->value;
        }
    }
    
    *error = EINVAL;
    return null;
}


static ptr_t get_property(int* error, void* m, size_t property) {
    Map map = (Map) m;
    
    switch (property) {
    case HASH_MAP_EQUALS:
        *error = ENONE;
        return (map->equals == default_equals) ? null : CODE(map->equals);
    case HASH_MAP_HASH:
        *error = ENONE;
        return (map->hash == default_hash) ? null : CODE(map->hash);
    default:
        *error = EINVAL;
        return null;
    }
}


static ptr_t put(int* error, void* m, ptr_t key, ptr_t value) {
    Map map = (Map) m;
    
    if ((map->size == SIZE_MAX) || (map->iterators > 0)) {
        *error = EPERM;
        return null;
    }
    if (initialize(error, map) != ENONE) {
        return null;
    }
    if (map->size >= (size_t) (map->load_factor * map->capacity)) {
        /* Expand the table, if it fails try next time. */
        double_capacity(map);
    }
    
    return put_key(error, map, key, value);
}


static ptr_t remove(int* error, void* m, ptr_t key) {
    Map map = (Map) m;
    
    if (map->iterators > 0) {
        *error = EPERM;
        return null;
    }
    if (initialize(error, map) != ENONE) {
        return null;
    }
    
    return remove_key(error, map, key);
}


static void set_property(int* error, void* m, size_t property, ptr_t value) {
    Map map = (Map) m;
    
    switch (property) {
    case HASH_MAP_EQUALS:
        if (value.code == NULL) {
            map->equals = default_equals;
        }
        else {
            map->equals = (Hash_Map_Equals) value.code;
        }
        *error = ENONE;
        break;
    case HASH_MAP_HASH:
        if (value.code == NULL) {
            map->hash = default_hash;
        }
        else {
            map->hash = (Hash_Map_Hash) value.code;
        }
        *error = ENONE;
        break;
    default:
        *error = EINVAL;
        break;
    }
}


static size_t size(int* error, void* m) {
    *error = ENONE;
    return ((Map) m)->size;
}


static void Iterator_to_end(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    iterator->position.bucket = iterator->map->capacity - 1;
    iterator->position.element = NULL;
    iterator->direction = BACKWARD;
    iterator->location = END;
    
    *error = ENONE;
}


static void Iterator_to_start(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    iterator->position.bucket = 0;
    iterator->position.element = NULL;
    iterator->direction = FORWARD;
    iterator->location = START;
    
    *error = ENONE;
}


static void* Iterator_create(int* error, void* collection) {
    Map map = (Map) collection;
    Iterator iterator;
    
    if (map->iterators == SIZE_MAX) {
        *error = EPERM;
        return NULL;
    }
    
    iterator = (Iterator) malloc(sizeof(struct _Iterator));
    
    if (iterator == NULL) {
        *error = ENOMEM;
        return NULL;
    }
    
    iterator->map = map;
    ++map->iterators;
    
    Iterator_to_start(error, iterator);
    return iterator;
}


static void Iterator_destroy(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    
    --iterator->map->iterators;
    memset(iterator, 0, sizeof(struct _Iterator));
    free(iterator);
    
    *error = ENONE;
}


static bool Iterator_has_next(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    *error = ENONE;
    return (iterator->map->size > 0) && (iterator->location != END);
}


static bool Iterator_has_previous(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    *error = ENONE;
    return (iterator->map->size > 0) && (iterator->location != START);
}


static ptr_t Iterator_next(int* error, void* it) {
    Iterator iterator = (Iterator) it;
    ptr_t key;
    
    if (!Iterator_has_next(error, iterator)) {
        *error = EPERM;
        return null;
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
    
    key = iterator->position.element->key;
    
    if (!get_next(iterator->position, NULL, iterator->map)) {
        Iterator_to_end(error, iterator);
    }
    
    *error = ENONE;
    return key;
}


static ptr_t Iterator_previous(int* error, UNUSED void* it) {
    Iterator iterator = (Iterator) it;
    ptr_t key;
    
    if (!Iterator_has_previous(error, iterator)) {
        *error = EPERM;
        return null;
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
    
    key = iterator->position.element->key;
    
    if (!get_previous(iterator->position, NULL, iterator->map)) {
        Iterator_to_start(error, iterator);
    }
    
    *error = ENONE;
    return key;
}


static const struct _Iterator_Implementation keys_iterator_implementation = {
    Iterator_create,
    Iterator_destroy,
    Iterator_to_end,
    Iterator_to_start,
    Iterator_has_next,
    Iterator_has_previous,
    Iterator_next,
    Iterator_previous
};


static const struct _Map_Implementation implementation = {
    (Iterator_Implementation) &keys_iterator_implementation,
    create,
    destroy,
    get,
    get_property,
    put,
    remove,
    set_property,
    size
};


const Map_Implementation Hash_Map = (Map_Implementation) &implementation;


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


bool Hash_Map_stringz_equals(ptr_t x, ptr_t y) {
    return strcmp((char*) x.data, (char*) y.data) == 0;
}


size_t Hash_Map_stringz_hash(ptr_t key) {
    size_t length = strlen((char*) key.data) * sizeof(char);
    return Hash_Map_hash((uint8_t*) key.data, length);
}
