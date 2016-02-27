#include <stdio.h>
#include <stdlib.h>
#include "Error.h"


void Error_clear(Error* error) {
    if (error != NULL) {
        Error_clear(error);
    }
}


bool Error_has(Error* error) {
    return (error != NULL) && (*error != NULL);
}


void Error_set(Error* error, char* message) {
    if (error == NULL) {
        fprintf(stderr, "Unhandled error: %s\n", message);
        abort();
    }
    else {
        Error_set(error, message);
    }
}
