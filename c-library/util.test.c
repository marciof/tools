#include "std/string.h"
#include "test.h"
#include "util.h"


static void concatenate(UNUSED ptr_t p) {
    const char* string = "123";
    
    assert_equals(strcmp(CONCATENATE(str, ing), string), 0);
    assert_equals(CONCATENATE(123, 45), 12345);
    
    assert_equals(CONCATENATE_INDIRECT(__LINE__, 3), 123);
}


static void convert_to_string(UNUSED ptr_t p) {
    assert_equals(strcmp(TO_STRING(123), "123"), 0);
    assert_equals(strcmp(TO_STRING(symbol), "symbol"), 0);
    
    assert_equals(strcmp(TO_STRING_INDIRECT(__LINE__), "20"), 0);
}


static void get_array_length(UNUSED ptr_t p) {
    int length_1[1], length_10[10];
    
    assert_equals(LENGTH_OF(length_1), 1);
    assert_equals(LENGTH_OF(length_10), 10);
}


static void get_function_name(UNUSED ptr_t p) {
    assert_equals(strcmp(FUNCTION_NAME, "get_function_name"), 0);
}


static void pack_structure(UNUSED ptr_t p) {
    PACKED(struct Packed_Type {
        char x;
        int y;
    });
    
    struct Padded_Type {
        char x;
        int y;
    };
    
    assert_equals(sizeof(struct Packed_Type), sizeof(int) + sizeof(char));
    assert_equals(sizeof(struct Padded_Type), 2 * sizeof(int));
}


struct Test_Parameter test_parameters[] = {{NULL, NULL}};


Test tests[] = {
    concatenate,
    convert_to_string,
    
    get_array_length,
    get_function_name,
    
    pack_structure,
    
    NULL
};
