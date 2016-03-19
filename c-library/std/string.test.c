#include "../test.h"
#include "../util.h"
#include "string.h"


static void check_empty_string_is_prefix_of_empty_string(UNUSED ptr_t p) {
    assert_true(strprefix("", ""));
    assert_equals(errno, ENONE);
}


static void check_empty_string_is_prefix_of_string(UNUSED ptr_t p) {
    assert_true(strprefix("123", ""));
    assert_equals(errno, ENONE);
}


static void check_empty_string_is_suffix_of_empty_string(UNUSED ptr_t p) {
    assert_true(strsuffix("", ""));
    assert_equals(errno, ENONE);
}


static void check_empty_string_is_suffix_of_string(UNUSED ptr_t p) {
    assert_true(strsuffix("123", ""));
    assert_equals(errno, ENONE);
}


static void check_string_is_not_prefix_of_empty_string(UNUSED ptr_t p) {
    assert_false(strprefix("", "123"));
    assert_equals(errno, ENONE);
}


static void check_string_is_not_suffix_of_empty_string(UNUSED ptr_t p) {
    assert_false(strsuffix("", "123"));
    assert_equals(errno, ENONE);
}


static void check_string_prefixes(UNUSED ptr_t p) {
    assert_false(strprefix("123", "45"));
    assert_equals(errno, ENONE);
    
    assert_false(strprefix("123", "12345"));
    assert_equals(errno, ENONE);
    
    assert_true(strprefix("123", "123"));
    assert_equals(errno, ENONE);
    
    assert_true(strprefix("123", "1"));
    assert_equals(errno, ENONE);
}


static void check_string_suffixes(UNUSED ptr_t p) {
    assert_false(strsuffix("123", "45"));
    assert_equals(errno, ENONE);
    
    assert_false(strsuffix("123", "12345"));
    assert_equals(errno, ENONE);
    
    assert_true(strsuffix("123", "123"));
    assert_equals(errno, ENONE);
    
    assert_true(strsuffix("123", "3"));
    assert_equals(errno, ENONE);
}


static void duplicate_empty_string(UNUSED ptr_t p) {
    char* string = strcopy("");
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, ""), 0);
    
    free(string);
}


static void duplicate_string(UNUSED ptr_t p) {
    char* string = strcopy("12345");
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, "12345"), 0);
    
    free(string);
}


static void format_empty_string(UNUSED ptr_t p) {
    char* string = strformat("");
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, ""), 0);
    
    free(string);
}


static void format_string(UNUSED ptr_t p) {
    char* string = strformat("Testing%s %d, %d, %d%c", "...", 1, 2, 3, '!');
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, "Testing... 1, 2, 3!"), 0);
    
    free(string);
}


static void join_array(UNUSED ptr_t p) {
    const char* STRINGS[] = {"Hello", "world!"};
    char* string = strjoin(LENGTH_OF(STRINGS), STRINGS, " ");
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, "Hello world!"), 0);
    
    free(string);
}


static void join_array_using_empty_separator(UNUSED ptr_t p) {
    const char* STRINGS[] = {"123", "45"};
    char* string = strjoin(LENGTH_OF(STRINGS), STRINGS, "");
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, "12345"), 0);
    
    free(string);
}


static void join_empty_array(UNUSED ptr_t p) {
    char* string = strjoin(0, NULL, " ");
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, ""), 0);
    
    free(string);
}


static void join_empty_array_using_empty_separator(UNUSED ptr_t p) {
    char* string = strjoin(0, NULL, "");
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, ""), 0);
    
    free(string);
}


static void partially_duplicate_empty_string(UNUSED ptr_t p) {
    char* string = strncopy("", 0);
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, ""), 0);
    
    free(string);
}


static void partially_duplicate_full_string(UNUSED ptr_t p) {
    char* string = strncopy("12345", 5);
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, "12345"), 0);
    
    free(string);
}


static void partially_duplicate_string(UNUSED ptr_t p) {
    char* string = strncopy("12345", 3);
    
    assert_not_null(string);
    assert_equals(errno, ENONE);
    assert_equals(strcmp(string, "123"), 0);
    
    free(string);
}


static void split_empty_string(UNUSED ptr_t p) {
    size_t length;
    char** strings = strsplit("", "-", &length);
    
    assert_not_null(strings);
    assert_equals(errno, ENONE);
    assert_equals(length, 0);
    assert_null(strings[length]);
    
    free(strings);
}


static void split_empty_string_using_empty_separator(UNUSED ptr_t p) {
    size_t length;
    char** strings = strsplit("", "", &length);
    
    assert_not_null(strings);
    assert_equals(errno, ENONE);
    assert_equals(length, 0);
    assert_null(strings[length]);
    
    free(strings);
}


static void split_string(UNUSED ptr_t p) {
    size_t length;
    const char* EXPECTED[] = {"1", "2", "3", "4", "5"};
    char** strings = strsplit(" 1 2       3 4  5 ", " ", &length);
    size_t i;
    
    assert_not_null(strings);
    assert_equals(errno, ENONE);
    assert_equals(length, LENGTH_OF(EXPECTED));
    assert_null(strings[length]);
    
    for (i = 0; i < length; ++i) {
        assert_equals(strcmp(strings[i], EXPECTED[i]), 0);
        free(strings[i]);
    }
    
    free(strings);
}


static void split_string_using_empty_separator(UNUSED ptr_t p) {
    size_t length;
    const char* EXPECTED[] = {"1", "2", "3", "4", "5"};
    char** strings = strsplit("12345", "", &length);
    size_t i;
    
    assert_not_null(strings);
    assert_equals(errno, ENONE);
    assert_equals(length, LENGTH_OF(EXPECTED));
    assert_null(strings[length]);
    
    for (i = 0; i < length; ++i) {
        assert_equals(strcmp(strings[i], EXPECTED[i]), 0);
        free(strings[i]);
    }
    
    free(strings);
}


static void split_string_without_separator(UNUSED ptr_t p) {
    size_t length;
    const char* EXPECTED[] = {"12345"};
    char** strings = strsplit("12345", " ", &length);
    size_t i;
    
    assert_not_null(strings);
    assert_equals(errno, ENONE);
    assert_equals(length, LENGTH_OF(EXPECTED));
    assert_null(strings[length]);
    
    for (i = 0; i < length; ++i) {
        assert_equals(strcmp(strings[i], EXPECTED[i]), 0);
        free(strings[i]);
    }
    
    free(strings);
}


struct Test_Parameter test_parameters[] = {{NULL, NULL}};


Test tests[] = {
    join_empty_array_using_empty_separator,
    join_empty_array,
    
    join_array_using_empty_separator,
    join_array,
    
    partially_duplicate_empty_string,
    partially_duplicate_string,
    partially_duplicate_full_string,
    
    split_empty_string_using_empty_separator,
    split_empty_string,
    
    split_string_using_empty_separator,
    split_string,
    split_string_without_separator,
    
    duplicate_empty_string,
    duplicate_string,
    
    check_empty_string_is_prefix_of_empty_string,
    check_empty_string_is_prefix_of_string,
    
    check_string_is_not_prefix_of_empty_string,
    check_string_prefixes,
    
    check_empty_string_is_suffix_of_empty_string,
    check_empty_string_is_suffix_of_string,
    
    check_string_is_not_suffix_of_empty_string,
    check_string_suffixes,
    
    format_empty_string,
    format_string,
    
    NULL
};
