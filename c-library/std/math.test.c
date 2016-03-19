#include "../test.h"
#include "math.h"


static void check_bits(UNUSED ptr_t p) {
    assert_true(BIT_IS_SET(BIT(0), 0));
    assert_true(BIT_IS_SET(BIT(1), 1));
    
    assert_false(BIT_IS_SET(BIT(0), 1));
    assert_false(BIT_IS_SET(BIT(1), 0));
    
    assert_true(BIT_IS_SET(BIT(0) + BIT(1), 0));
    assert_true(BIT_IS_SET(BIT(0) + BIT(1), 1));
    
    assert_false(BIT_IS_SET(BIT(0) + BIT(1), 2));
    assert_false(BIT_IS_SET(BIT(0) + BIT(1), 3));
}


static void clear_bits(UNUSED ptr_t p) {
    assert_equals(BIT_CLEAR(BIT(0), 0), 0);
    assert_equals(BIT_CLEAR(BIT(1), 1), 0);
    
    assert_equals(BIT_CLEAR(BIT(0) + BIT(1), 1), BIT(0));
    assert_equals(BIT_CLEAR(BIT(0) + BIT(1) + BIT(2), 1), BIT(0) + BIT(2));
}


static void compute_maximum_value(UNUSED ptr_t p) {
    assert_equals(MAX(0, 0), 0);
    
    assert_equals(MAX(0, 1), 1);
    assert_equals(MAX(1, 0), 1);
    
    assert_equals(MAX(0, -1), 0);
    assert_equals(MAX(-1, 0), 0);
}


static void compute_minimum_value(UNUSED ptr_t p) {
    assert_equals(MIN(0, 0), 0);
    
    assert_equals(MIN(0, 1), 0);
    assert_equals(MIN(1, 0), 0);
    
    assert_equals(MIN(0, -1), -1);
    assert_equals(MIN(-1, 0), -1);
}


static void create_bits(UNUSED ptr_t p) {
    assert_equals(BIT(0), 1);
    assert_equals(BIT(1), 2);
    assert_equals(BIT(2), 4);
}


static void get_bits(UNUSED ptr_t p) {
    assert_equals(BIT_GET(BIT(0), 0), BIT(0));
    assert_equals(BIT_GET(BIT(1), 1), BIT(1));
    
    assert_equals(BIT_GET(BIT(0) + BIT(1), 1), BIT(1));
    assert_equals(BIT_GET(BIT(0) + BIT(1) + BIT(2), 1), BIT(1));
}


static void set_bits(UNUSED ptr_t p) {
    assert_equals(BIT_SET(BIT(0), 0), BIT(0));
    assert_equals(BIT_SET(BIT(1), 1), BIT(1));
    
    assert_equals(BIT_SET(0, 0), BIT(0));
    assert_equals(BIT_SET(0, 1), BIT(1));
    
    assert_equals(BIT_SET(BIT(1), 0), BIT(0) + BIT(1));
    assert_equals(BIT_SET(BIT(0) + BIT(2), 1), BIT(0) + BIT(1) + BIT(2));
}


struct Test_Parameter test_parameters[] = {{NULL, NULL}};


Test tests[] = {
    compute_maximum_value,
    compute_minimum_value,
    
    create_bits,
    clear_bits,
    get_bits,
    set_bits,
    check_bits,
    
    NULL
};
