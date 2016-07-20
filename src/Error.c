#include <string.h>
#include <sys/types.h>
#include "Error.h"

void Error_add(Error* error, const char* message) {
    for (ssize_t i = ERROR_MESSAGE_STACK_SIZE - 1 - 1; i >= 0; --i) {
        (*error)[i+1] = (*error)[i];
    }

    (*error)[0] = message;
}

void Error_set(Error* error, Error* source) {
    for (size_t i = 0; i < ERROR_MESSAGE_STACK_SIZE; ++i) {
        (*error)[i] = (*source)[i];
    }
}

void Error_print(Error* error, FILE* stream) {
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
