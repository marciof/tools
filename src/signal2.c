#define _POSIX_C_SOURCE 199309L
#include <errno.h>
#include <stdbool.h>
#include <stdlib.h>
#include "Array.h"
#include "signal2.h"

struct Handler {
    int signum;
    intptr_t arg;
    void (*callback)(int signum, intptr_t arg);
};

struct Array handlers = ARRAY_NULL_INITIALIZER;

static void signal2_handler(int signum) {
    for (size_t i = 0; i < handlers.length; ++i) {
        struct Handler* handler = (struct Handler*) handlers.data[i];

        if (handler->signum == signum) {
            handler->callback(signum, handler->arg);
        }
    }
}

void signal2(
        int signum,
        intptr_t arg,
        void (*callback)(int signum, intptr_t arg),
        struct Error* error) {

    struct sigaction current_sa;

    if (sigaction(signum, NULL, &current_sa) == -1) {
        Error_add_errno(error, errno);
        return;
    }

    bool has_foreign_handler
        = ((current_sa.sa_flags & SA_SIGINFO) != 0)
        || ((current_sa.sa_handler != NULL)
            && (current_sa.sa_handler != signal2_handler));

    if (has_foreign_handler) {
        Error_add_string(error, "foreign sigaction handler already installed");
        return;
    }

    struct Handler* handler = (struct Handler*) malloc(sizeof(*handler));

    if (handler == NULL) {
        Error_add_errno(error, errno);
        return;
    }

    handler->signum = signum;
    handler->arg = arg;
    handler->callback = callback;

    if (ARRAY_IS_NULL_INITIALIZED(&handlers)) {
        Array_init(&handlers, error, handler, NULL);
    }
    else {
        Array_add(&handlers, handlers.length, (intptr_t) handler, error);
    }

    if (Error_has(error)) {
        free(handler);
        return;
    }

    struct sigaction new_sa;

    sigemptyset(&new_sa.sa_mask);
    new_sa.sa_handler = signal2_handler;
    new_sa.sa_flags = 0;

    if (sigaction(signum, &new_sa, NULL) == -1) {
        Error_add_errno(error, errno);
        free(handler);
        return;
    }
}
