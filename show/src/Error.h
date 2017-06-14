#pragma once
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define ERROR_STACK_SIZE 8
#define ERROR_INITIALIZER {{0}, {NULL}}

/** Ordered by most to least recent error message. */
struct Error {
    intptr_t arg[ERROR_STACK_SIZE];
    char* (*describe[ERROR_STACK_SIZE])(intptr_t arg);
};

void Error_add(struct Error* error, char* (*describe)(intptr_t), intptr_t arg);
void Error_add_errno(struct Error* error, int nr);
void Error_add_string(struct Error* error, char* message);

void Error_clear(struct Error* error);
void Error_copy(struct Error* error, struct Error* source);

bool Error_has(struct Error* error);
bool Error_has_errno(struct Error* error, int nr);

/** @return `true` if there was an error, or `false` otherwise */
bool Error_print(struct Error* error, FILE* stream);
