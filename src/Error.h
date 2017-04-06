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

void Error_add(Error* error, char* (*describe)(intptr_t), intptr_t arg);
void Error_add_errno(Error* error, int nr);
void Error_add_string(Error* error, char* message);

void Error_clear(Error* error);
void Error_copy(Error* error, Error* source);
bool Error_has(Error* error);

/**
 * @return `true` if there was an error, or `false` otherwsie
 */
bool Error_print(Error* error, FILE* stream);
