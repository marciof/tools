#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include "../list/Array_List.h"
#include "Map.h"


struct _Map {
    Map_Impl impl;
    void* map;
};


void Map_delete(Map map, Error* error) {
    if (map != NULL) {
        map->impl->destroy(map->map, error);
        
        if (*error) {
            return;
        }

        memset(map, 0, sizeof(struct _Map));
        free(map);
    }
    
    *error = NULL;
}


intptr_t Map_get(Map map, intptr_t key, Error* error) {
    return map->impl->get(map->map, key, error);
}


intptr_t Map_get_property(Map map, size_t property, Error* error) {
    return map->impl->get_property(map->map, property, error);
}


bool Map_has_key(Map map, intptr_t key) {
    Error error;
    Map_get(map, key, &error);
    return !*error;
}


List Map_keys(Map map, Error* error) {
    List keys = List_new(Array_List, error);

    if (*error) {
        return NULL;
    }
    
    Iterator keys_iterator = Map_keys_iterator(map, error);
    
    if (*error) {
        List_delete(keys, error);
        *error = strerror(ENOMEM);
        return NULL;
    }
    
    while (Iterator_has_next(keys_iterator)) {
        intptr_t key = Iterator_next(keys_iterator, error);
        Error discard;

        if (*error) {
            List_delete(keys, &discard);
            Iterator_delete(keys_iterator);
            return NULL;
        }

        List_add(keys, key, error);
        
        if (*error) {
            List_delete(keys, &discard);
            Iterator_delete(keys_iterator);
            return NULL;
        }
    }

    Iterator_delete(keys_iterator);
    *error = NULL;
    return keys;
}


Iterator Map_keys_iterator(Map map, Error* error) {
    return Iterator_new(map->impl->keys_iterator, map->map, error);
}


Map Map_new(Map_Impl implementation, Error* error) {
    Map map = (Map) malloc(sizeof(struct _Map));

    if (map == NULL) {
        *error = strerror(ENOMEM);
        return NULL;
    }
    
    map->impl = implementation;
    map->map = implementation->create(error);
    
    if (*error) {
        free(map);
        return NULL;
    }
    
    *error = NULL;
    return map;
}


intptr_t Map_put(Map map, intptr_t key, intptr_t value, Error* error) {
    return map->impl->put(map->map, key, value, error);
}


intptr_t Map_remove(Map map, intptr_t key, Error* error) {
    return map->impl->remove(map->map, key, error);
}


bool Map_set_property(Map map, size_t property, intptr_t value, Error* error) {
    map->impl->set_property(map->map, property, value, error);
    return !*error;
}


size_t Map_size(Map map) {
    return map->impl->size(map->map);
}


List Map_values(Map map, Error* error) {
    List values = List_new(Array_List, error);

    if (*error) {
        return NULL;
    }
    
    Iterator keys_iterator = Map_keys_iterator(map, error);
    Error discard;

    if (*error) {
        List_delete(values, &discard);
        return NULL;
    }
    
    while (Iterator_has_next(keys_iterator)) {
        intptr_t key = Iterator_next(keys_iterator, error);

        if (*error) {
            List_delete(values, &discard);
            Iterator_delete(keys_iterator);
            return NULL;
        }

        List_add(values, Map_get(map, key, &discard), error);
        
        if (*error) {
            List_delete(values, &discard);
            Iterator_delete(keys_iterator);
            return NULL;
        }
    }

    Iterator_delete(keys_iterator);
    *error = NULL;
    return values;
}
