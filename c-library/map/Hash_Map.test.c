#include "../test.h"
#include "../util.h"
#include "Hash_Map.h"
#include "Map.h"


static size_t f1(void) {
    return 1;
}


static size_t f2(void) {
    return 2;
}


static size_t f3(void) {
    return 3;
}


/**
 * Compares two function pointers.
 *
 * @param [in] x first function pointer
 * @param [in] y second function pointer
 * @return @c true if both pointers refer to the same function or @c false
 *         otherwise
 */
static bool function_equals(ptr_t x, ptr_t y) {
    return x.code == y.code;
}


/**
 * Computes the hash code of a function pointer.
 *
 * @param [in] function function pointer to hash
 * @return hash code for the given function pointer
 */
static size_t function_hash(ptr_t function) {
    return (size_t) function.code;
}


static void get_set_invalid_properties(UNUSED ptr_t p) {
    Map map = Map_new(Hash_Map);
    ptr_t value = CODE(Hash_Map_stringz_equals);
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get_property(map, HASH_MAP_EQUALS - 1).code, null.code);
    assert_equals(errno, EINVAL);
    
    assert_false(Map_set_property(map, HASH_MAP_EQUALS - 1, value));
    assert_equals(errno, EINVAL);
    
    assert_equals(Map_get_property(map, HASH_MAP_EQUALS - 1).code, null.code);
    assert_equals(errno, EINVAL);
    
    assert_equals(Map_get_property(map, HASH_MAP_HASH + 1).code, null.code);
    assert_equals(errno, EINVAL);
    
    assert_false(Map_set_property(map, HASH_MAP_HASH + 1, value));
    assert_equals(errno, EINVAL);
    
    assert_equals(Map_get_property(map, HASH_MAP_HASH + 1).code, null.code);
    assert_equals(errno, EINVAL);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void get_set_properties(UNUSED ptr_t p) {
    Map map = Map_new(Hash_Map);
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get_property(map, HASH_MAP_EQUALS).code, null.code);
    assert_equals(errno, ENONE);
    
    assert_true(Map_set_property(map, HASH_MAP_EQUALS,
        CODE(Hash_Map_stringz_equals)));
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get_property(map, HASH_MAP_EQUALS).code,
        CODE(Hash_Map_stringz_equals).code);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get_property(map, HASH_MAP_HASH).code, null.code);
    assert_equals(errno, ENONE);
    
    assert_true(Map_set_property(map, HASH_MAP_HASH,
        CODE(Hash_Map_stringz_hash)));
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get_property(map, HASH_MAP_HASH).code,
        CODE(Hash_Map_stringz_hash).code);
    assert_equals(errno, ENONE);
    
    assert_true(Map_set_property(map, HASH_MAP_EQUALS, null));
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get_property(map, HASH_MAP_EQUALS).code, null.code);
    assert_equals(errno, ENONE);
    
    assert_true(Map_set_property(map, HASH_MAP_HASH, null));
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get_property(map, HASH_MAP_HASH).code, null.code);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void use_function_pointers_as_keys(UNUSED ptr_t p) {
    typedef size_t (*Function)(void);
    
    Map map = Map_new(Hash_Map);
    Function keys[] = {f1, f2, f3};
    size_t expected[] = {1, 2, 3};
    size_t i;
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    assert_equals(LENGTH_OF(keys), LENGTH_OF(expected));
    
    assert_true(Map_set_property(map, HASH_MAP_EQUALS, CODE(function_equals)));
    assert_equals(errno, ENONE);
    
    assert_true(Map_set_property(map, HASH_MAP_HASH, CODE(function_hash)));
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(expected); ++i) {
        assert_equals(Map_put(map, CODE(keys[i]), DATA(expected[i])).data,
            null.data);
        assert_equals(errno, ENONE);
    }
    
    for (i = 0; i < LENGTH_OF(expected); ++i) {
        size_t n = (size_t) Map_get(map, CODE(keys[i])).data;
        
        assert_equals(n, expected[i]);
        assert_equals(n, keys[i]());
    }
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


static void use_properties(UNUSED ptr_t p) {
    Map map = Map_new(Hash_Map);
    const char key_1[] = "Key";
    const char key_2[] = "Key";
    const char* value = "Value";
    
    assert_not_null(map);
    assert_equals(errno, ENONE);
    
    assert_not_equals(key_1, key_2);
    assert_true(Hash_Map_stringz_equals(DATA(key_1), DATA(key_2)));
    
    assert_true(Map_set_property(map, HASH_MAP_EQUALS,
        CODE(Hash_Map_stringz_equals)));
    assert_equals(errno, ENONE);
    
    assert_true(Map_set_property(map, HASH_MAP_HASH,
        CODE(Hash_Map_stringz_hash)));
    assert_equals(errno, ENONE);
    
    assert_false(Map_has_key(map, DATA(key_1)));
    assert_equals(errno, ENONE);
    
    assert_false(Map_has_key(map, DATA(key_2)));
    assert_equals(errno, ENONE);
    
    assert_equals(Map_put(map, DATA(key_1), DATA(value)).data, null.data);
    assert_equals(errno, ENONE);
    
    assert_equals(Map_get(map, DATA(key_2)).data, value);
    assert_equals(errno, ENONE);
    
    Map_delete(map);
    assert_equals(errno, ENONE);
}


struct Test_Parameter test_parameters[] = {{NULL, NULL}};


Test tests[] = {
    get_set_invalid_properties,
    get_set_properties,
    use_properties,
    use_function_pointers_as_keys,
    
    NULL
};
