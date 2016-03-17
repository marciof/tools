#include "Array.h"
#include "Array.test.h"

START_TEST(test_array)
{
    int numbers[] = {-1, 0, 1};
    ck_assert_int_eq(STATIC_ARRAY_LENGTH(numbers), 3);
}
END_TEST

START_TEST(test_string)
{
    char text[] = "abc";
    ck_assert_int_eq(STATIC_ARRAY_LENGTH(text), 3 + 1);
}
END_TEST

Suite* std_array_suite() {
    Suite* suite = suite_create("std/array");
    TCase* tcase = tcase_create("STATIC_ARRAY_LENGTH");

    tcase_add_test(tcase, test_array);
    tcase_add_test(tcase, test_string);
    suite_add_tcase(suite, tcase);

    return suite;
}
