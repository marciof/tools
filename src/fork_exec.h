#pragma once
#include "Error.h"

int fork_exec_fd(char* file, char* argv[], int* pid, Error* error);
int fork_exec_status(char* file, char* argv[], Error* error);
