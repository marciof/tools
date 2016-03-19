#include "../list/List.h"
#include "../test.h"
#include "../util.h"
#include "Hash_Map.h"
#include "Map.h"


/**
 * Comparison function to sort a list of strings in alphabetic order.
 *
 * @param [in] x first string
 * @param [in] y second string
 * @return negative number, zero, or a positive number if the first element is
 *         considered to be respectively less than, equal to, or greater than
 *         the second
 */
static int alphabetically(ptr_t x, ptr_t y) {
    return strcmp((char*) x.data, (char*) y.data);
}


static size_t f1(void) {
    return 1;
}


static size_t f2(void) {
    return 2;
}


static size_t f3(void) {
    return 3;
}


static void check_iterator_has_next_on_empty_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_false(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void check_iterator_has_next(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_put(map, DATA("Key"), DATA("Value")).data, null.data);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_true(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void check_iterator_has_previous_on_empty_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void check_iterator_has_previous(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_put(map, DATA("Key"), DATA("Value")).data, null.data);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void check_values(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    const char* key = "Key";
    const char* value = "Value";
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_false(Map_has_key(map, DATA(key)));
    assert_equals(errno, ENONE);
    
    assert_equals(Map_put(map, DATA(key), DATA(value)).data, null.data);
    assert_equals(errno, ENONE);
    assert_equals(Map_size(map), 1);
    
    assert_true(Map_has_key(map, DATA(key)));
    assert_equals(errno, ENONE);
    
    assert_equals(Map_remove(map, DATA(key)).data, value);
    assert_equals(errno, ENONE);
    assert_equals(Map_size(map), 0);
    
    assert_false(Map_has_key(map, DATA(key)))
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void create_and_delete(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_size(map), 0);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void create_and_delete_iterator(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void create_and_delete_iterator_after_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void delete_null(UNUSED ptr_t implementation) {
    Map_delete(NULL);
    assert_equals(errno, ENONE);
}


static void delete_null_iterator(UNUSED ptr_t implementation) {
    Iterator_delete(NULL);
    assert_equals(errno, ENONE);
}


static void delete_while_iterating(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_put(map, DATA("Key"), DATA("Value")).data, null.data);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, EPERM);
    assert_equals(Map_size(map), 1);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void get_invalid_values(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get(map, DATA("Unknown key.")).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(Map_size(map), 0);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void get_keys(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    const char* keys[] = {"a", "b", "c"};
    const char* values[] = {"1", "2", "3"};
    List all_keys;
    size_t i;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(keys), LENGTH_OF(values));
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_equals(Map_put(map, DATA(keys[i]), DATA(values[i])).data,
            null.data);
        assert_equals(errno, ENONE);
    }
    
    all_keys = Map_keys(map);
    assert_not_null(all_keys);
    assert_equals(errno, ENONE);
    
    List_sort(all_keys, alphabetically);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_equals(List_get(all_keys, i).data, keys[i]);
    }
    
    List_delete(all_keys);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void get_keys_from_empty_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    List keys;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    keys = Map_keys(map);
    assert_not_null(keys);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_size(map), 0);
    assert_equals(List_length(keys), 0);
    
    List_delete(keys);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void get_values(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    const char* keys[] = {"a", "b", "c"};
    const char* values[] = {"1", "2", "3"};
    List all_values;
    size_t i;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(keys), LENGTH_OF(values));
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_equals(Map_put(map, DATA(keys[i]), DATA(values[i])).data,
            null.data);
        assert_equals(errno, ENONE);
    }
    
    all_values = Map_values(map);
    assert_not_null(all_values);
    assert_equals(errno, ENONE);
    
    List_sort(all_values, alphabetically);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_equals(List_get(all_values, i).data, values[i]);
    }
    
    List_delete(all_values);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void get_values_from_empty_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    List values;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    values = Map_values(map);
    assert_not_null(values);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_size(map), 0);
    assert_equals(List_length(values), 0);
    
    List_delete(values);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void iterate_backward(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    const char* keys[] = {"a", "b", "c"};
    const char* values[] = {"1", "2", "3"};
    size_t i;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(keys), LENGTH_OF(values));
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_equals(Map_put(map, DATA(keys[i]), DATA(values[i])).data,
            null.data);
        assert_equals(errno, ENONE);
    }
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void iterate_backward_from_end(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    const char* keys[] = {"a", "b", "c"};
    const char* values[] = {"1", "2", "3"};
    ssize_t i;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(keys), LENGTH_OF(values));
    
    for (i = 0; i < (ssize_t) LENGTH_OF(keys); ++i) {
        assert_equals(Map_put(map, DATA(keys[i]), DATA(values[i])).data,
            null.data);
        assert_equals(errno, ENONE);
    }
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    Iterator_to_end(iterator);
    assert_equals(errno, ENONE);
    
    for (i = LENGTH_OF(keys) - 1; Iterator_has_previous(iterator); ++i) {
        size_t j;
        char* key = (char*) Iterator_previous(iterator).data;
        assert_equals(errno, ENONE);
        
        /* The keys might not be stored in the same order as they were added. */
        for (j = 0; j < LENGTH_OF(keys); ++j) {
            if (keys[j] == key) {
                keys[j] = NULL;
                break;
            }
        }
    }
    
    /* All keys were seen if all elements are NULL. */
    for (i = 0; i < (ssize_t) LENGTH_OF(keys); ++i) {
        assert_null(keys[i]);
    }
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void iterate_backward_on_empty_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void iterate_empty_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    assert_false(Iterator_has_previous(iterator));
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_previous(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void iterate_forward(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    const char* keys[] = {"a", "b", "c"};
    const char* values[] = {"1", "2", "3"};
    size_t i;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(keys), LENGTH_OF(values));
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_equals(Map_put(map, DATA(keys[i]), DATA(values[i])).data,
            null.data);
        assert_equals(errno, ENONE);
    }
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    for (i = 0; Iterator_has_next(iterator); ++i) {
        size_t j;
        char* key = (char*) Iterator_next(iterator).data;
        assert_equals(errno, ENONE);
        
        /* The keys might not be stored in the same order as they were added. */
        for (j = 0; j < LENGTH_OF(keys); ++j) {
            if (keys[j] == key) {
                keys[j] = NULL;
                break;
            }
        }
    }
    
    /* All keys were seen if all elements are NULL. */
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_null(keys[i]);
    }
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void iterate_forward_from_start(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    const char* keys[] = {"a", "b", "c"};
    const char* values[] = {"1", "2", "3"};
    size_t i;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(keys), LENGTH_OF(values));
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_equals(Map_put(map, DATA(keys[i]), DATA(values[i])).data,
            null.data);
        assert_equals(errno, ENONE);
    }
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    Iterator_to_start(iterator);
    assert_equals(errno, ENONE);
    
    for (i = 0; Iterator_has_next(iterator); ++i) {
        size_t j;
        char* key = (char*) Iterator_next(iterator).data;
        assert_equals(errno, ENONE);
        
        /* The keys might not be stored in the same order as they were added. */
        for (j = 0; j < LENGTH_OF(keys); ++j) {
            if (keys[j] == key) {
                keys[j] = NULL;
                break;
            }
        }
    }
    
    /* All keys were seen if all elements are NULL. */
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_null(keys[i]);
    }
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void iterate_forward_on_empty_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_equals(errno, ENONE);
    
    assert_equals(Iterator_next(iterator).data, null.data);
    assert_equals(errno, EPERM);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void iterate_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    const char* keys[] = {"a", "b", "c"};
    const char* values[] = {"1", "2", "3"};
    const char* seen[LENGTH_OF(keys)];
    size_t i;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(keys), LENGTH_OF(values));
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        seen[i] = NULL;
        assert_equals(Map_put(map, DATA(keys[i]), DATA(values[i])).data,
            null.data);
        assert_equals(errno, ENONE);
    }
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    while (Iterator_has_next(iterator)) {
        size_t j;
        char* key = (char*) Iterator_next(iterator).data;
        assert_equals(errno, ENONE);
        
        assert_equals(Iterator_previous(iterator).data, key);
        assert_equals(errno, ENONE);
        
        assert_equals(Iterator_next(iterator).data, key);
        assert_equals(errno, ENONE);
        
        /* The keys might not be stored in the same order as they were added. */
        for (j = 0; j < LENGTH_OF(keys); ++j) {
            if (keys[j] == key) {
                seen[j] = key;
                break;
            }
        }
    }
    
    /* All keys were seen unless an element is NULL. */
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_not_null(seen[i]);
        
        /* Reset for the next iteration. */
        seen[i] = NULL;
    }
    
    while (Iterator_has_previous(iterator)) {
        size_t j;
        char* key = (char*) Iterator_previous(iterator).data;
        assert_equals(errno, ENONE);
        
        assert_equals(Iterator_next(iterator).data, key);
        assert_equals(errno, ENONE);
        
        assert_equals(Iterator_previous(iterator).data, key);
        assert_equals(errno, ENONE);
        
        /* Ditto. */
        for (j = 0; j < LENGTH_OF(keys); ++j) {
            if (keys[j] == key) {
                seen[j] = key;
                break;
            }
        }
    }
    
    /* All keys were seen unless an element is NULL. */
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_not_null(seen[i]);
    }
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void move_iterator_to_end_on_empty_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_false(Iterator_has_previous(iterator));
    
    Iterator_to_end(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_false(Iterator_has_previous(iterator));
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void move_iterator_to_start_on_empty_map(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_false(Iterator_has_previous(iterator));
    
    Iterator_to_start(iterator);
    assert_equals(errno, ENONE);
    
    assert_false(Iterator_has_next(iterator));
    assert_false(Iterator_has_previous(iterator));
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void put_many_values(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    size_t i;
    const char* keys[] = {
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
        "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
    };
    const char* values[] = {
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
        "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
    };
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(keys), LENGTH_OF(values));
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_equals(Map_put(map, DATA(keys[i]), DATA(values[i])).data,
            null.data);
        assert_equals(errno, ENONE);
        assert_equals(Map_size(map), i + 1);
    }
    
    for (i = 0; i < LENGTH_OF(keys); ++i) {
        assert_equals(Map_get(map, DATA(keys[i])).data, values[i]);
        assert_equals(errno, ENONE);
    }
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void put_value_while_iterating(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_put(map, DATA("Key"), DATA("Value")).data, null.data);
    assert_equals(errno, EPERM);
    assert_equals(Map_size(map), 0);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void put_values(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    const char* key_1 = "Key 1";
    const char* key_2 = "Key 2";
    const char* value_1 = "Value 1";
    const char* value_2 = "Value 2";
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get(map, DATA(key_1)).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(Map_get(map, DATA(key_2)).data, null.data);
    assert_equals(errno, EINVAL);
    assert_equals(Map_size(map), 0);
    
    assert_equals(Map_put(map, DATA(key_1), DATA(value_1)).data, null.data);
    assert_equals(errno, ENONE);
    assert_equals(Map_size(map), 1);
    
    assert_equals(Map_put(map, DATA(key_2), DATA(value_2)).data, null.data);
    assert_equals(errno, ENONE);
    assert_equals(Map_size(map), 2);
    
    assert_equals(Map_put(map, DATA(key_1), DATA(value_2)).data, value_1);
    assert_equals(errno, ENONE);
    assert_equals(Map_size(map), 2);
    
    assert_equals(Map_put(map, DATA(key_2), DATA(value_1)).data, value_2);
    assert_equals(errno, ENONE);
    assert_equals(Map_size(map), 2);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void remove_value_while_iterating(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    const char* key = "Key";
    Iterator iterator;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_put(map, DATA(key), DATA("Value")).data, null.data);
    assert_equals(errno, ENONE);
    
    iterator = Map_keys_iterator(map);
    assert_not_null(iterator);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_remove(map, DATA(key)).data, null.data);
    assert_equals(errno, EPERM);
    assert_equals(Map_size(map), 1);
    
    Iterator_delete(iterator);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void remove_values(ptr_t implementation) {
    Map map = Map_new((Map_Implementation) implementation.data);
    const char* key = "Key";
    const char* value = "Value";
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get(map, DATA(key)).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(Map_remove(map, DATA(key)).data, null.data);
    assert_equals(errno, EINVAL);
    assert_equals(Map_size(map), 0);
    
    assert_equals(Map_put(map, DATA(key), DATA(value)).data, null.data);
    assert_equals(errno, ENONE);
    assert_equals(Map_size(map), 1);
    
    assert_equals(Map_get(map, DATA(key)).data, value);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_remove(map, DATA(key)).data, value);
    assert_equals(errno, ENONE);
    assert_equals(Map_size(map), 0);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void use_function_pointers_as_values(ptr_t implementation) {
    typedef size_t (*Function)(void);
    
    Map map = Map_new((Map_Implementation) implementation.data);
    Function values[] = {f1, f2, f3};
    size_t expected[] = {1, 2, 3};
    size_t i;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(values), LENGTH_OF(expected));
    
    for (i = 0; i < LENGTH_OF(expected); ++i) {
        assert_equals(Map_put(map, DATA(expected[i]), CODE(values[i])).data,
            null.data);
        assert_equals(errno, ENONE);
    }
    
    for (i = 0; i < LENGTH_OF(expected); ++i) {
        Function f = (Function) Map_get(map, DATA(expected[i])).code;
        
        assert_equals(f, values[i]);
        assert_equals(f(), expected[i]);
    }
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static ptr_t get_Hash_Map(void) {
    return DATA(Hash_Map);
}

struct Test_Parameter test_parameters[] = {
    {"Hash_Map", get_Hash_Map},
    {NULL, NULL}
};


Test tests[] = {
    /* Map: */
    
    create_and_delete,
    delete_null,
    
    put_values,
    put_many_values,
    get_invalid_values,
    remove_values,
    check_values,
    
    get_keys_from_empty_map,
    get_keys,
    get_values_from_empty_map,
    get_values,
    use_function_pointers_as_values,
    
    /* Map iterator: */
    
    create_and_delete_iterator,
    delete_null_iterator,
    create_and_delete_iterator_after_map,
    
    check_iterator_has_next_on_empty_map,
    check_iterator_has_previous_on_empty_map,
    check_iterator_has_next,
    check_iterator_has_previous,
    
    move_iterator_to_end_on_empty_map,
    move_iterator_to_start_on_empty_map,
    
    iterate_backward_on_empty_map,
    iterate_forward_on_empty_map,
    iterate_backward,
    iterate_forward,
    
    iterate_backward_from_end,
    iterate_forward_from_start,
    iterate_empty_map,
    iterate_map,
    
    delete_while_iterating,
    put_value_while_iterating,
    remove_value_while_iterating,
    
    NULL
};
