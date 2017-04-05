#pragma once
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define ERROR_MESSAGE_STACK_SIZE 8
#define ERROR_INITIALIZER {{NULL, 0}}

struct Error_Cause {
    char* (*describe)(intptr_t arg);
    intptr_t arg;
};

// Successful calls must not clear errors.
// Ordered by most to least recent error message.
typedef struct Error_Cause Error[ERROR_MESSAGE_STACK_SIZE];

#define ERROR_ADD_ERRNO(/* Error* */ error, /* int */ num) \
    Error_add((error), Error_describe_errno, (num))

#define ERROR_ADD_STRING(/* Error* */ error, /* char* */ message) \
    Error_add((error), Error_describe_string, (intptr_t) (message))

#define ERROR_CLEAR(/* Error* */ error) \
    ((void) ((*(error))[0].describe = NULL))

#define ERROR_GET_LAST(/* Error* */ error) \
    ((*(error))[0])

#define /* bool */ ERROR_HAS(/* Error* */ error) \
    ((*(error))[0].describe != NULL)

void Error_add(Error* error, char* (*describe)(intptr_t), intptr_t arg);
void Error_copy(Error* error, Error* source);
char* Error_describe_errno(intptr_t arg);
char* Error_describe_string(intptr_t arg);

/**
 * @return `true` if there was an error, or `false` otherwsie
 */
bool Error_print(Error* error, FILE* stream);
