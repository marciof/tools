#pragma once
#include <signal.h>
#include <stdint.h>
#include "Error.h"

/** Non-thread safe. */
void signal2(
    int signum,
    intptr_t arg,
    void (*callback)(int signum, intptr_t arg),
    struct Error* error);
