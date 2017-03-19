#pragma once
#include <stdbool.h>
#include <sys/types.h>
#include "Error.h"

int popen2(
    char* file,
    char* argv[],
    int out_fd,
    int err_fd,
    pid_t* pid,
    Error* error);

int popen2_pipe(
    char* file,
    char* argv[],
    int out_fd,
    int err_fd,
    bool is_for_reading,
    pid_t* pid,
    Error* error);

bool popen2_can_run(char* file, Error* error);
int popen2_status(char* file, char* argv[], Error* error);
int wait_subprocess(pid_t child_pid, Error* error);
