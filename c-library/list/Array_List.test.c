#include "../test.h"
#include "../util.h"
#include "Array_List.h"
#include "List.h"


static void get_set_invalid_properties(UNUSED ptr_t p) {
    List list = List_new(Array_List);
    const char* value = "Value";
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    assert_equals(List_get_property(list, ARRAY_LIST_CAPACITY - 1).data,
        null.data);
    assert_equals(errno, EINVAL);
    
    assert_false(List_set_property(list, ARRAY_LIST_CAPACITY - 1, DATA(value)));
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get_property(list, ARRAY_LIST_CAPACITY - 1).data,
        null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get_property(list, ARRAY_LIST_CAPACITY + 1).data,
        null.data);
    assert_equals(errno, EINVAL);
    
    assert_false(List_set_property(list, ARRAY_LIST_CAPACITY + 1, DATA(value)));
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get_property(list, ARRAY_LIST_CAPACITY + 1).data,
        null.data);
    assert_equals(errno, EINVAL);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void get_set_properties(UNUSED ptr_t p) {
    List list = List_new(Array_List);
    const char* elements[] = {"a", "b", "c"};
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    List_get_property(list, ARRAY_LIST_CAPACITY);
    assert_equals(errno, ENONE);
    
    assert_false(List_set_property(list, ARRAY_LIST_CAPACITY,
        DATA(LENGTH_OF(elements) - 1)));
    assert_equals(errno, EINVAL);
    
    assert_true(List_set_property(list, ARRAY_LIST_CAPACITY,
        DATA(LENGTH_OF(elements))));
    assert_equals(errno, ENONE);
    
    assert_equals((size_t) List_get_property(list, ARRAY_LIST_CAPACITY).data,
        LENGTH_OF(elements));
    assert_equals(errno, ENONE);
    
    assert_true(List_set_property(list, ARRAY_LIST_CAPACITY,
        DATA(LENGTH_OF(elements) + 1)));
    assert_equals(errno, ENONE);
    
    assert_equals((size_t) List_get_property(list, ARRAY_LIST_CAPACITY).data,
        LENGTH_OF(elements) + 1);
    assert_equals(errno, ENONE);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


static void sort_large_array(UNUSED ptr_t p) {
    List list = List_new(Array_List);
    size_t elements[] = {
        1, 26, 5, 20, 0, 23, 7, 23, 11, 21,
        15, 29, 4, 6, 10, 13, 12, 1, 14, 26,
        4, 23, 21, 0, 25, 0, 13, 23, 10, 24
    };
    size_t previous = 0;
    size_t i;
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        List_add(list, DATA(elements[i]));
        assert_equals(errno, ENONE);
    }
    
    List_sort(list, NULL);
    assert_equals(errno, ENONE);
    
    for (i = 0; i < LENGTH_OF(elements); ++i) {
        size_t current = (size_t) List_get(list, i).data;
        
        assert_true(previous <= current);
        previous = current;
    }
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


struct Test_Parameter test_parameters[] = {{NULL, NULL}};


Test tests[] = {
    get_set_invalid_properties,
    get_set_properties,
    sort_large_array,
    
    NULL
};
