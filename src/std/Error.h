#pragma once
#include <stdbool.h>


typedef const char* Error;

void Error_clear(Error* error);
bool Error_has(Error* error);
void Error_set(Error* error, char* message);
