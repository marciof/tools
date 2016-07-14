#include <string.h>
#include "Error.h"

void Error_add(Error* error, const char* message) {
    memmove(
        (*error) + 1,
        *error,
        (ERROR_MESSAGE_STACK_SIZE - 1) * sizeof((*error)[0]));

    (*error)[0] = message;
}

void Error_set(Error* error, Error* source) {
    for (size_t i = 0; i < ERROR_MESSAGE_STACK_SIZE; ++i) {
        (*error)[i] = (*source)[i];
    }
}

void Error_print(FILE* stream, Error* error) {
    if (ERROR_HAS(error)) {
        for (size_t i = 0; i < ERROR_MESSAGE_STACK_SIZE; ++i) {
            const char* message = (*error)[i];

            if (message == NULL) {
                fprintf(stream, "\n");
                break;
            }

            if (i > 0) {
                fprintf(stream, ": ");
            }

            fprintf(stream, "%s", message);
        }
    }
}
