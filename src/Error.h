#pragma once
#include <stdbool.h>

typedef const char* Error;

void Error_clear(Error* error);
bool Error_has(Error* error);

/**
 * Wrapper around `Error_set`.
 */
void Error_errno(Error* error, int code);

/**
 * If `error` is `NULL`, an error message is displayed and `abort` is called.
 */
void Error_set(Error* error, char* message);
