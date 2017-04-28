#pragma once
#include <signal.h>
#include <stdint.h>
#include "Error.h"

/**
 * Non-reentrant.
 * @return pointer to `arg` location or `NULL` on error
 */
intptr_t* signal2_add(
    int signum,
    intptr_t arg,
    void (*callback)(int signum, intptr_t arg),
    struct Error* error);

/**
 * Removes first matching handler only.
 * Non-reentrant.
 */
void signal2_remove(
    int signum,
    intptr_t arg,
    void (*callback)(int signum, intptr_t arg),
    struct Error* error);
