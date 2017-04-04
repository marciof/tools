#include <string.h>
#include <sys/types.h>
#include "Error.h"

void Error_add(Error* error, char* (*describe)(intptr_t), intptr_t arg) {
    for (ssize_t i = ERROR_MESSAGE_STACK_SIZE - 1 - 1; i >= 0; --i) {
        (*error)[i + 1] = (*error)[i];
    }

    struct Error_Cause* cause = &(*error)[0];

    cause->describe = describe;
    cause->arg = arg;
}

void Error_copy(Error* error, Error* source) {
    for (size_t i = 0; i < ERROR_MESSAGE_STACK_SIZE; ++i) {
        (*error)[i] = (*source)[i];
    }
}

char* Error_describe_errno(intptr_t arg) {
    return strerror((int) arg);
}

char* Error_describe_string(intptr_t arg) {
    return (char*) arg;
}

bool Error_print(Error* error, FILE* stream) {
    if (ERROR_HAS(error)) {
        for (size_t i = 0; i < ERROR_MESSAGE_STACK_SIZE; ++i) {
            struct Error_Cause* cause = &(*error)[i];

            if (cause->describe == NULL) {
                fprintf(stream, "\n");
                break;
            }

            if (i > 0) {
                fprintf(stream, ": ");
            }

            fprintf(stream, "%s", cause->describe(cause->arg));
        }
        return true;
    }
    else {
        return false;
    }
}
