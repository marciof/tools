#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ptr.h"
#include "types.h"
#include "util.h"


#define __Test_assert_fail(assertion_type, assert_expression) \
    __Test_type = assertion_type; \
    __Test_file_name = __FILE__; \
    __Test_line_number = __LINE__; \
    __Test_test_name = FUNCTION_NAME; \
    __Test_expression = TO_STRING(assert_expression); \
    return


/**
 * Asserts that two values are equal.
 *
 * @param [in] x first value to compare with
 * @param [in] y second value to compare with
 */
#define assert_equals(x, y) \
    if ((x) != (y)) { \
        __Test_assert_fail("Assert equals", (x) == (y)); \
    }


/**
 * Asserts that a value is false.
 *
 * @param [in] value value to assert it's false
 */
#define assert_false(value) \
    if (value) { \
        __Test_assert_fail("Assert false", value); \
    }


/**
 * Asserts that two values aren't equal.
 *
 * @param [in] x first value to compare with
 * @param [in] y second value to compare with
 */
#define assert_not_equals(x, y) \
    if ((x) == (y)) { \
        __Test_assert_fail("Assert not equals", (x) != (y)); \
    }


/**
 * Asserts that a value isn't NULL.
 *
 * @param [in] value value to assert it isn't NULL
 */
#define assert_not_null(value) \
    if ((value) == NULL) { \
        __Test_assert_fail("Assert not null", value); \
    }


/**
 * Asserts that a value is NULL.
 *
 * @param [in] value value to assert it's NULL
 */
#define assert_null(value) \
    if ((value) != NULL) { \
        __Test_assert_fail("Assert null", value); \
    }


/**
 * Asserts that a value is true.
 *
 * @param [in] value value to assert it's true
 */
#define assert_true(value) \
    if (!(value)) { \
        __Test_assert_fail("Assert true", value); \
    }


typedef ptr_t (*Test_Parameter_Get)(void);
typedef void (*Test)(ptr_t parameter);

struct Test_Parameter {
    const char* name;
    Test_Parameter_Get get;
};


static const char* __Test_type = NULL;
static const char* __Test_file_name = NULL;
static unsigned long __Test_line_number = 0;
static const char* __Test_test_name = NULL;
static const char* __Test_expression = NULL;


extern struct Test_Parameter test_parameters[];
extern Test tests[];


static size_t __Test_run(ptr_t parameter) {
    unsigned long j, failed_tests;
    
    for (j = failed_tests = 0; tests[j] != NULL; ++j) {
        __Test_type = NULL;
        tests[j](parameter);
        
        if (__Test_type != NULL) {
            ++failed_tests;
            
            fprintf(stderr, "Assertion failed: %s \"%s\", in \"%s\", at %s:%lu\n",
                __Test_type, __Test_expression,
                __Test_test_name, __Test_file_name,
                __Test_line_number);
        }
    }
    
    printf("Total: %lu\n", j);
    
    if (failed_tests > 0) {
        printf("Failed: %lu\n", failed_tests);
    }
    
    return failed_tests;
}


int main(int nr_arguments, UNUSED char** arguments) {
    bool has_failed = false;
    
    if (nr_arguments > 1) {
        fprintf(stderr, "Error: Too many arguments.\n");
        return EXIT_FAILURE;
    }
    
    if (tests[0] == NULL) {
        fprintf(stderr, "Error: No tests found.\n");
        return EXIT_FAILURE;
    }
    
    if (test_parameters[0].name == NULL) {
        has_failed = (__Test_run(null) > 0);
    }
    else {
        size_t i, failed_tests = 0;
        
        for (i = 0; test_parameters[i].name != NULL; ++i) {
            ptr_t parameter = test_parameters[i].get();
            const char* name = test_parameters[i].name;
            
            printf("- Parameter \"%s\"\n", name);
            failed_tests += (__Test_run(parameter) > 0) ? 1 : 0;
        }
        
        has_failed = (failed_tests > 0);
    }
    
    return has_failed ? EXIT_FAILURE : EXIT_SUCCESS;
}
