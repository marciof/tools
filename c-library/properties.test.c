#include "properties.h"
#include "test.h"


static void get_set_invalid_properties(UNUSED ptr_t p) {
    ptr_t value = DATA(123);
    
    assert_equals(Eon_Library_get_property(EON_LIBRARY_MAJOR_VERSION - 1).data,
        null.data);
    assert_equals(errno, EINVAL);
    
    assert_false(Eon_Library_set_property(EON_LIBRARY_MAJOR_VERSION - 1,
        value));
    assert_equals(errno, EINVAL);
    
    assert_equals(Eon_Library_get_property(EON_LIBRARY_MAJOR_VERSION - 1).data,
        null.data);
    assert_equals(errno, EINVAL);
    
    assert_equals(Eon_Library_get_property(EON_LIBRARY_MICRO_VERSION + 1).data,
        null.data);
    assert_equals(errno, EINVAL);
    
    assert_false(Eon_Library_set_property(EON_LIBRARY_MICRO_VERSION + 1,
        value));
    assert_equals(errno, EINVAL);
    
    assert_equals(Eon_Library_get_property(EON_LIBRARY_MICRO_VERSION + 1).data,
        null.data);
    assert_equals(errno, EINVAL);
}


static void get_set_properties(UNUSED ptr_t p) {
    size_t version;
    
    version = (size_t) Eon_Library_get_property(EON_LIBRARY_MAJOR_VERSION).data;
    assert_equals(errno, ENONE);
    assert_true(version <= 9999);
    
    assert_false(Eon_Library_set_property(EON_LIBRARY_MAJOR_VERSION, null));
    assert_equals(errno, EINVAL);
    
    version = (size_t) Eon_Library_get_property(EON_LIBRARY_MINOR_VERSION).data;
    assert_equals(errno, ENONE);
    assert_true(version <= 12);
    
    assert_false(Eon_Library_set_property(EON_LIBRARY_MINOR_VERSION, null));
    assert_equals(errno, EINVAL);
    
    version = (size_t) Eon_Library_get_property(EON_LIBRARY_MICRO_VERSION).data;
    assert_equals(errno, ENONE);
    assert_true(version <= 31);
    
    assert_false(Eon_Library_set_property(EON_LIBRARY_MICRO_VERSION, null));
    assert_equals(errno, EINVAL);
}


struct Test_Parameter test_parameters[] = {{NULL, NULL}};


Test tests[] = {
    get_set_invalid_properties,
    get_set_properties,
    
    NULL
};
