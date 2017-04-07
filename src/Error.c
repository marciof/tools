#include <string.h>
#include <sys/types.h>
#include "Error.h"

static char* Error_describe_errno(intptr_t arg) {
    return strerror((int) arg);
}

static char* Error_describe_string(intptr_t arg) {
    return (char*) arg;
}

void Error_add(struct Error* error, char* (*describe)(intptr_t), intptr_t arg) {
    for (ssize_t i = ERROR_STACK_SIZE - 1 - 1; i >= 0; --i) {
        error->arg[i + 1] = error->arg[i];
        error->describe[i + 1] = error->describe[i];
    }

    error->arg[0] = arg;
    error->describe[0] = describe;
}

void Error_add_errno(struct Error* error, int nr) {
    Error_add(error, Error_describe_errno, nr);
}

void Error_add_string(struct Error* error, char* message) {
    Error_add(error, Error_describe_string, (intptr_t) message);
}

void Error_clear(struct Error* error) {
    error->describe[0] = NULL;
}

void Error_copy(struct Error* error, struct Error* source) {
    for (size_t i = 0; i < ERROR_STACK_SIZE; ++i) {
        error->arg[i] = source->arg[i];
        error->describe[i] = source->describe[i];
    }
}

bool Error_has(struct Error* error) {
    return error->describe[0] != NULL;
}

bool Error_has_errno(struct Error* error, int nr) {
    return (error->describe[0] == Error_describe_errno)
        && (error->arg[0] == nr);
}

bool Error_print(struct Error* error, FILE* stream) {
    if (!Error_has(error)) {
        return false;
    }

    for (size_t i = 0; i < ERROR_STACK_SIZE; ++i) {
        if (error->describe[i] == NULL) {
            fprintf(stream, "\n");
            break;
        }

        if (i > 0) {
            fprintf(stream, ": ");
        }

        fprintf(stream, "%s", error->describe[i](error->arg[i]));
    }

    return true;
}
