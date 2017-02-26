#pragma once
#include <sys/types.h>
#include "Error.h"

int fork_exec_fd(char* file, char* argv[], pid_t* pid, Error* error);
int fork_exec_status(char* file, char* argv[], Error* error);
