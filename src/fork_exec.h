#pragma once
#include "Error.h"

int fork_exec(char* file, char* argv[], int* pid, Error* error);
