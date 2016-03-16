#pragma once
#include <stdbool.h>

typedef const char* Error;

void Error_clear(Error* error);
void Error_errno(Error* error, int code);
bool Error_has(Error* error);
void Error_set(Error* error, char* message);
