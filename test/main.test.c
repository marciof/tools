#include <check.h>
#include <stdlib.h>
#include "Array.test.h"

int main() {
    SRunner* runner = srunner_create(NULL);

    srunner_add_suite(runner, std_array_suite());
    srunner_run_all(runner, CK_VERBOSE);

    int nr_failed = srunner_ntests_failed(runner);
    srunner_free(runner);
    return (nr_failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
