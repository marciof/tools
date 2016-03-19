#include "../list/Array_List.h"
#include "../std/stdlib.h"
#include "../std/string.h"
#include "Map.h"


struct _Map {
    Map_Implementation implementation;
    void* map;
};


void Map_delete(Map map) {
    if (map != NULL) {
        int error;
        map->implementation->destroy(&error, map->map);
        
        if (error != ENONE) {
            errno = error;
            return;
        }
        
        memset(map, 0, sizeof(struct _Map));
        free(map);
    }
    
    errno = ENONE;
}


ptr_t Map_get(Map map, ptr_t key) {
    int error;
    ptr_t value = map->implementation->get(&error, map->map, key);
    
    errno = error;
    return value;
}


ptr_t Map_get_property(Map map, size_t property) {
    int error;
    ptr_t value = map->implementation->get_property(&error, map->map, property);
    
    errno = error;
    return value;
}


bool Map_has_key(Map map, ptr_t key) {
    Map_get(map, key);
    
    if (errno == ENOMEM) {
        return false;
    }
    else if (errno == EINVAL) {
        errno = ENONE;
        return false;
    }
    else {
        return true;
    }
}


List Map_keys(Map map) {
    List keys = List_new(Array_List);
    Iterator keys_iterator;
    
    if (errno == ENOMEM) {
        return NULL;
    }
    
    keys_iterator = Map_keys_iterator(map);
    
    if (keys_iterator == NULL) {
        List_delete(keys);
        errno = ENOMEM;
        return NULL;
    }
    
    while (Iterator_has_next(keys_iterator)) {
        List_add(keys, Iterator_next(keys_iterator));
        
        if (errno == ENOMEM) {
            List_delete(keys);
            Iterator_delete(keys_iterator);
            
            errno = ENOMEM;
            return NULL;
        }
    }
    
    Iterator_delete(keys_iterator);
    errno = ENONE;
    return keys;
}


Iterator Map_keys_iterator(Map map) {
    return Iterator_new(map->implementation->keys_iterator, map->map);
}


Map Map_new(Map_Implementation implementation) {
    Map map = (Map) malloc(sizeof(struct _Map));
    int error;
    
    if (map == NULL) {
        errno = ENOMEM;
        return NULL;
    }
    
    map->implementation = implementation;
    map->map = implementation->create(&error);
    
    if (error != ENONE) {
        free(map);
        errno = error;
        return NULL;
    }
    
    errno = ENONE;
    return map;
}


ptr_t Map_put(Map map, ptr_t key, ptr_t value) {
    int error;
    ptr_t prev_value = map->implementation->put(&error, map->map, key, value);
    
    errno = error;
    return prev_value;
}


ptr_t Map_remove(Map map, ptr_t key) {
    int error;
    ptr_t value = map->implementation->remove(&error, map->map, key);
    
    errno = error;
    return value;
}


bool Map_set_property(Map map, size_t property, ptr_t value) {
    int error;
    
    map->implementation->set_property(&error, map->map, property, value);
    errno = error;
    
    return error == ENONE;
}


size_t Map_size(Map map) {
    int error;
    
    errno = ENONE;
    return map->implementation->size(&error, map->map);
}


List Map_values(Map map) {
    List values = List_new(Array_List);
    Iterator keys_iterator;
    
    if (errno == ENOMEM) {
        return NULL;
    }
    
    keys_iterator = Map_keys_iterator(map);
    
    if (keys_iterator == NULL) {
        List_delete(values);
        errno = ENOMEM;
        return NULL;
    }
    
    while (Iterator_has_next(keys_iterator)) {
        List_add(values, Map_get(map, Iterator_next(keys_iterator)));
        
        if (errno == ENOMEM) {
            List_delete(values);
            Iterator_delete(keys_iterator);
            
            errno = ENOMEM;
            return NULL;
        }
    }
    
    Iterator_delete(keys_iterator);
    errno = ENONE;
    return values;
}
