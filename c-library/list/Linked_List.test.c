#include "../test.h"
#include "../util.h"
#include "Linked_List.h"
#include "List.h"


static void get_set_invalid_properties(UNUSED ptr_t p) {
    List list = List_new(Linked_List);
    const char* value = "Value";
    
    assert_not_null(list);
    assert_equals(errno, ENONE);
    
    assert_equals(List_get_property(list, (size_t) -1).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_false(List_set_property(list, (size_t) -1, DATA(value)));
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get_property(list, (size_t) -1).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get_property(list, 0).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_false(List_set_property(list, 0, DATA(value)));
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get_property(list, 0).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get_property(list, 1).data, null.data);
    assert_equals(errno, EINVAL);
    
    assert_false(List_set_property(list, 1, DATA(value)));
    assert_equals(errno, EINVAL);
    
    assert_equals(List_get_property(list, 1).data, null.data);
    assert_equals(errno, EINVAL);
    
    List_delete(list);
    assert_equals(errno, ENONE);
}


struct Test_Parameter test_parameters[] = {{NULL, NULL}};


Test tests[] = {
    get_set_invalid_properties,
    NULL
};
