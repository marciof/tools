#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include "../io.h"
#include "Pager_Plugin.h"

#define EXTERNAL_BINARY "pager"

static struct winsize terminal;

static void out_close(intptr_t arg) {
}

static void out_write(
        intptr_t arg, uint8_t** data, size_t* length, Error* error) {

    io_write((int) arg, *data, *length, error);
    *data = NULL;
    *length = 0;
}

static Array* create_argv(Array* options, Error* error) {
    Array* argv = Array_new(error, EXTERNAL_BINARY, NULL);

    if (Error_has(error)) {
        return NULL;
    }

    if (options != NULL) {
        Array_extend(argv, options, error);

        if (Error_has(error)) {
            Array_delete(argv);
            return NULL;
        }
    }

    Array_add(argv, (intptr_t) NULL, error);

    if (Error_has(error)) {
        Array_delete(argv);
        return NULL;
    }

    Error_clear(error);
    return argv;
}

static void create_output(int fd, Array* outputs, Error* error) {
    Output* output = Output_new(error);

    if (Error_has(error)) {
        return;
    }

    output->arg = (intptr_t) fd;
    output->close = out_close;
    output->write = out_write;

    Array_add(outputs, (intptr_t) output, error);

    if (Error_has(error)) {
        Output_delete(output);
        return;
    }

    Error_clear(error);
}

static const char* get_description() {
    return "page output via `" EXTERNAL_BINARY "`";
}

static const char* get_name() {
    return EXTERNAL_BINARY;
}

static void get_terminal_size(int num) {
    signal(SIGWINCH, get_terminal_size);
    ioctl(STDOUT_FILENO, TIOCGWINSZ, &terminal);
}

static void run(Array* inputs, Array* options, Array* outputs, Error* error) {
    if (!isatty(STDOUT_FILENO)) {
        Error_clear(error);
        return;
    }
    if (signal(SIGWINCH, get_terminal_size) == SIG_ERR) {
        Error_errno(error, errno);
        return;
    }
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &terminal) == -1) {
        Error_errno(error, errno);
        return;
    }

    int read_write_fds[2];

    if (pipe(read_write_fds) == -1) {
        Error_errno(error, errno);
        return;
    }

    create_output(read_write_fds[1], outputs, error);
    if (Error_has(error)) {
        return;
    }

    int child_pid = fork();

    if (child_pid == -1) {
        Error_errno(error, errno);
        return;
    }
    else if (!child_pid) {
        close(read_write_fds[0]);
        Error_clear(error);
        return;
    }

    if (dup2(read_write_fds[0], STDIN_FILENO) == -1) {
        Error_errno(error, errno);
        return;
    }

    Array* argv = create_argv(options, error);
    if (Error_has(error)) {
        return;
    }

    close(read_write_fds[0]);
    close(read_write_fds[1]);
    execvp((char*) argv->data[0], (char**) argv->data);
    Error_errno(error, errno);
    Array_delete(argv);
}

Plugin Pager_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
