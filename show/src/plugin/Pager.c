#include <unistd.h>
#include "../io.h"
#include "../popen2.h"
#include "../signal2.h"
#include "Pager.h"

// Don't use `pager` as it's not available on all systems.
#define EXTERNAL_BINARY "less"

#define INVALID_PID ((pid_t) -1)

static void close_output(struct Output* output, struct Error* error) {
    popen2_close(output->fd, (pid_t) output->arg, error);
}

static size_t write_output(
        struct Output* output,
        char* buffer,
        size_t length,
        struct Error* error) {

    io_write_all(output->fd, buffer, length * sizeof(buffer[0]), error);
    return Error_has(error) ? 0 : length;
}

static bool is_available(struct Plugin* plugin, struct Error* error) {
    char* argv[] = {
        EXTERNAL_BINARY,
        "--version",
        NULL,
    };

    return popen2_check(argv[0], argv, error);
}

// FIXME: remove signal handler when child exists
// FIXME: not currently being called on Ctrl+C in the child
static void sigint_handler(int signum, intptr_t arg) {
}

static void open_input(
        struct Plugin* plugin,
        struct Input* input,
        size_t argc,
        char* argv[],
        struct Error* error) {
}

// FIXME: pass-through signals, such as Ctrl+C
static void open_output(
        struct Plugin* plugin,
        struct Output* output,
        size_t argc,
        char* argv[],
        struct Error* error) {

    bool is_tty = io_is_tty(STDOUT_FILENO, error);

    if (Error_has(error) || !is_tty) {
        return;
    }

    intptr_t* signal_arg = signal2_add(
        SIGINT, INVALID_PID, sigint_handler, error);

    if (Error_has(error)) {
        return;
    }

    char* exec_argv[1 + argc + 1];
    exec_argv[0] = EXTERNAL_BINARY;
    exec_argv[0 + 1 + argc] = "--";
    exec_argv[0 + 1 + argc + 1] = NULL;

    for (size_t i = 0; i < argc; ++i) {
        exec_argv[0 + 1 + i] = argv[i];
    }

    output->fd = popen2(
        exec_argv[0],
        exec_argv,
        false,
        IO_NULL_FD,
        IO_NULL_FD,
        (pid_t*) &output->arg,
        error);

    if (Error_has(error)) {
        Error_add_string(error, "`" EXTERNAL_BINARY "`");
        signal2_remove(SIGINT, INVALID_PID, sigint_handler, error);
        return;
    }

    output->close = close_output;
    output->write = write_output;
    *signal_arg = output->arg;
}

struct Plugin Pager_Plugin = {
    "pager",
    "page output via `" EXTERNAL_BINARY "`, when needed",
    is_available,
    open_input,
    open_output,
};
