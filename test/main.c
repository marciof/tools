#include <check.h>
#include <stdlib.h>
#include "std/array.h"


START_TEST(test_array) {
    int numbers[] = {-1, 0, 1};
    ck_assert_int_eq(STATIC_ARRAY_LENGTH(numbers), 3);
}
END_TEST


START_TEST(test_string) {
    char text[] = "abc";
    ck_assert_int_eq(STATIC_ARRAY_LENGTH(text), 4);
}
END_TEST


Suite* array_suite() {
    Suite* suite = suite_create("array");
    TCase* tcase = tcase_create(NULL);

    tcase_add_test(tcase, test_array);
    tcase_add_test(tcase, test_string);
    suite_add_tcase(suite, tcase);

    return suite;
}


int main() {
    Suite* suite = array_suite();
    SRunner* runner = srunner_create(suite);

    srunner_run_all(runner, CK_VERBOSE);
    int nr_failed = srunner_ntests_failed(runner);
    srunner_free(runner);

    return (nr_failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
