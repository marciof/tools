#include <string.h>
#include <sys/types.h>
#include "Error.h"

static char* Error_describe_errno(intptr_t arg) {
    return strerror((int) arg);
}

static char* Error_describe_string(intptr_t arg) {
    return (char*) arg;
}

void Error_add(Error* error, char* (*describe)(intptr_t), intptr_t arg) {
    for (ssize_t i = ERROR_MESSAGE_STACK_SIZE - 1 - 1; i >= 0; --i) {
        (*error)[i + 1] = (*error)[i];
    }

    struct Error_Cause* cause = &(*error)[0];

    cause->arg = arg;
    cause->describe = describe;
}

void Error_add_errno(Error* error, int nr) {
    Error_add(error, Error_describe_errno, nr);
}

void Error_add_string(Error* error, char* message) {
    Error_add(error, Error_describe_string, (intptr_t) message);
}

void Error_clear(Error* error) {
    (*error)[0].describe = NULL;
}

void Error_copy(Error* error, Error* source) {
    for (size_t i = 0; i < ERROR_MESSAGE_STACK_SIZE; ++i) {
        (*error)[i] = (*source)[i];
    }
}

bool Error_has(Error* error) {
    return (*error)[0].describe != NULL;
}

bool Error_has_errno(Error* error, int nr) {
    struct Error_Cause* cause = &(*error)[0];
    return (cause->describe == Error_describe_errno)
        && (cause->arg == nr);
}

bool Error_print(Error* error, FILE* stream) {
    if (!Error_has(error)) {
        return false;
    }

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
