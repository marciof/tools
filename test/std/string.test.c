#include "string.test.h"
#include "std/string.h"


START_TEST(test_empty_is_prefix_of_empty_string)
{
    ck_assert(strprefix("", ""));
}
END_TEST


START_TEST(test_empty_is_prefix_of_non_empty_string)
{
    ck_assert(strprefix("123", ""));
}
END_TEST


START_TEST(test_string_is_not_prefix_of_empty_string)
{
    ck_assert(!strprefix("", "123"));
}
END_TEST


START_TEST(test_string_prefixes)
{
    ck_assert(!strprefix("123", "45"));
    ck_assert(!strprefix("123", "12345"));
    ck_assert(strprefix("123", "123"));
    ck_assert(strprefix("123", "1"));
}
END_TEST


Suite* std_string_suite() {
    Suite* suite = suite_create("std/string");
    TCase* strprefix_tcase = tcase_create("strprefix");

    tcase_add_test(strprefix_tcase, test_empty_is_prefix_of_empty_string);
    tcase_add_test(strprefix_tcase, test_empty_is_prefix_of_non_empty_string);
    tcase_add_test(strprefix_tcase, test_string_is_not_prefix_of_empty_string);
    tcase_add_test(strprefix_tcase, test_string_prefixes);
    suite_add_tcase(suite, strprefix_tcase);

    return suite;
}
