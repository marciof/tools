#include <check.h>
#include <stdlib.h>
#include "std/array.test.h"


int main() {
    Suite* suite = std_array_suite();
    SRunner* runner = srunner_create(suite);

    srunner_run_all(runner, CK_VERBOSE);
    int nr_failed = srunner_ntests_failed(runner);
    srunner_free(runner);

    return (nr_failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
