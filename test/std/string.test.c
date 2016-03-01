#include "string.test.h"
#include "std/array.h"
#include "std/string.h"


START_TEST(test_copy_empty_string)
{
    Error error;
    char* string = strcopy("", &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "");

    free(string);
}
END_TEST


START_TEST(test_copy_non_empty_string)
{
    Error error;
    char* string = strcopy("12345", &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "12345");

    free(string);
}
END_TEST


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


START_TEST(test_format_empty_string)
{
    Error error;
    char* string = strformat("", &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "");

    free(string);
}
END_TEST


START_TEST(test_format_non_empty_string)
{
    Error error;
    char* string = strformat(
        "Testing%s %d, %d, %d%c", &error, "...", 1, 2, 3, '!');

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "Testing... 1, 2, 3!");

    free(string);
}
END_TEST


START_TEST(test_join_array)
{
    Error error;
    const char* STRINGS[] = {"Hello", "world", "!"};
    char* string = strjoin(STATIC_ARRAY_LENGTH(STRINGS), STRINGS, " ", &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "Hello world !");

    free(string);
}
END_TEST


START_TEST(test_join_array_using_empty_separator)
{
    Error error;
    const char* STRINGS[] = {"123", "45"};
    char* string = strjoin(STATIC_ARRAY_LENGTH(STRINGS), STRINGS, "", &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "12345");

    free(string);
}
END_TEST


START_TEST(test_join_empty_array)
{
    Error error;
    char* string = strjoin(0, NULL, " ", &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "");

    free(string);
}
END_TEST


START_TEST(test_join_empty_array_using_empty_separator)
{
    Error error;
    char* string = strjoin(0, NULL, "", &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "");

    free(string);
}
END_TEST


START_TEST(test_partial_copy_empty_string)
{
    Error error;
    char* string = strncopy("", 0, &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "");

    free(string);
}
END_TEST


START_TEST(test_partial_copy_full_string)
{
    Error error;
    char* string = strncopy("12345", 5, &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "12345");

    free(string);
}
END_TEST


START_TEST(test_partial_copy_string)
{
    Error error;
    char* string = strncopy("12345", 3, &error);

    ck_assert_ptr_ne(string, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_str_eq(string, "123");

    free(string);
}
END_TEST


START_TEST(test_split_empty_string)
{
    Error error;
    size_t length;
    char** strings = strsplit("", "-", &length, &error);

    ck_assert_ptr_ne(strings, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_int_eq(length, 0);
    ck_assert_ptr_eq(strings[length], NULL);

    free(strings);
}
END_TEST


START_TEST(test_split_empty_string_with_empty_separator)
{
    Error error;
    size_t length;
    char** strings = strsplit("", "", &length, &error);

    ck_assert_ptr_ne(strings, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_int_eq(length, 0);
    ck_assert_ptr_eq(strings[length], NULL);

    free(strings);
}
END_TEST


START_TEST(test_split_string)
{
    Error error;
    size_t length;
    const char* EXPECTED[] = {"1", "2", "3", "4", "5"};
    char** strings = strsplit(" 1 2       3 4  5 ", " ", &length, &error);

    ck_assert_ptr_ne(strings, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_int_eq(length, STATIC_ARRAY_LENGTH(EXPECTED));
    ck_assert_ptr_eq(strings[length], NULL);

    for (size_t i = 0; i < length; ++i) {
        ck_assert_str_eq(strings[i], EXPECTED[i]);
        free(strings[i]);
    }

    free(strings);
}
END_TEST


START_TEST(test_split_string_with_empty_separator)
{
    Error error;
    size_t length;
    const char* EXPECTED[] = {"1", "2", "3", "4", "5"};
    char** strings = strsplit("12345", "", &length, &error);

    ck_assert_ptr_ne(strings, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_int_eq(length, STATIC_ARRAY_LENGTH(EXPECTED));
    ck_assert_ptr_eq(strings[length], NULL);

    for (size_t i = 0; i < length; ++i) {
        ck_assert_str_eq(strings[i], EXPECTED[i]);
        free(strings[i]);
    }

    free(strings);
}
END_TEST


START_TEST(test_split_string_without_separator)
{
    Error error;
    size_t length;
    const char* EXPECTED[] = {"12345"};
    char** strings = strsplit("12345", " ", &length, &error);

    ck_assert_ptr_ne(strings, NULL);
    ck_assert(!Error_has(&error));
    ck_assert_int_eq(length, STATIC_ARRAY_LENGTH(EXPECTED));
    ck_assert_ptr_eq(strings[length], NULL);

    for (size_t i = 0; i < length; ++i) {
        ck_assert_str_eq(strings[i], EXPECTED[i]);
        free(strings[i]);
    }

    free(strings);
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

    TCase* strcopy_tcase = tcase_create("strcopy");
    TCase* strformat_tcase = tcase_create("strformat");
    TCase* strjoin_tcase = tcase_create("strjoin");
    TCase* strncopy_tcase = tcase_create("strncopy");
    TCase* strprefix_tcase = tcase_create("strprefix");
    TCase* strsplit_tcase = tcase_create("strsplit");

    tcase_add_test(strcopy_tcase, test_copy_empty_string);
    tcase_add_test(strcopy_tcase, test_copy_non_empty_string);

    tcase_add_test(strformat_tcase, test_format_empty_string);
    tcase_add_test(strformat_tcase, test_format_non_empty_string);

    tcase_add_test(strjoin_tcase, test_join_array);
    tcase_add_test(strjoin_tcase, test_join_array_using_empty_separator);
    tcase_add_test(strjoin_tcase, test_join_empty_array);
    tcase_add_test(strjoin_tcase, test_join_empty_array_using_empty_separator);

    tcase_add_test(strncopy_tcase, test_partial_copy_empty_string);
    tcase_add_test(strncopy_tcase, test_partial_copy_full_string);
    tcase_add_test(strncopy_tcase, test_partial_copy_string);

    tcase_add_test(strprefix_tcase, test_empty_is_prefix_of_empty_string);
    tcase_add_test(strprefix_tcase, test_empty_is_prefix_of_non_empty_string);
    tcase_add_test(strprefix_tcase, test_string_is_not_prefix_of_empty_string);
    tcase_add_test(strprefix_tcase, test_string_prefixes);

    tcase_add_test(strsplit_tcase, test_split_empty_string);
    tcase_add_test(strsplit_tcase, test_split_empty_string_with_empty_separator);
    tcase_add_test(strsplit_tcase, test_split_string);
    tcase_add_test(strsplit_tcase, test_split_string_with_empty_separator);
    tcase_add_test(strsplit_tcase, test_split_string_without_separator);

    suite_add_tcase(suite, strcopy_tcase);
    suite_add_tcase(suite, strformat_tcase);
    suite_add_tcase(suite, strjoin_tcase);
    suite_add_tcase(suite, strncopy_tcase);
    suite_add_tcase(suite, strprefix_tcase);
    suite_add_tcase(suite, strsplit_tcase);

    return suite;
}
