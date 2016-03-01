#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "Error.h"


void Error_clear(Error* error) {
    if (error != NULL) {
        *error = NULL;
    }
}


void Error_errno(Error* error, int code) {
    Error_set(error, strerror(code));
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
        *error = message;
    }
}
