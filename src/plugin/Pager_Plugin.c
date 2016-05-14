#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include "../Array.h"
#include "../io.h"
#include "Pager_Plugin.h"

#define EXTERNAL_BINARY "pager"
#define PAGING_THRESHOLD 0.5

typedef struct {
    Array buffer;
    Array* options;
    size_t nr_lines;
    size_t nr_line_chars;
    int fd;
} Pager;

static struct winsize terminal;

static void Pager_delete(Pager* pager) {
    if (pager != NULL) {
        for (size_t i = 0; i < pager->buffer.length; ++i) {
            free((void*) pager->buffer.data[i]);
        }
        Array_deinit(&pager->buffer);
        memset(pager, 0, sizeof(*pager));
        free(pager);
    }
}

static Pager* Pager_new(Array* options, Error* error) {
    Pager* pager = (Pager*) malloc(sizeof(*pager));

    if (pager == NULL) {
        ERROR_ERRNO(error, errno);
        return NULL;
    }

    pager->options = options;
    pager->nr_lines = 0;
    pager->nr_line_chars = 0;
    pager->fd = IO_INVALID_FD;

    Array_init(&pager->buffer, error, NULL);

    if (ERROR_HAS(error)) {
        free(pager);
        return NULL;
    }

    return pager;
}

static bool buffer_pager_input(
        Pager* pager, char** data, size_t* length, Error* error) {

    bool should_buffer = true;

    for (size_t i = 0; i < *length; ++i) {
        if ((*data)[i] == '\n') {
            ++pager->nr_lines;
            pager->nr_line_chars = 0;

            if (pager->nr_lines > (terminal.ws_row * PAGING_THRESHOLD)) {
                should_buffer = false;
                break;
            }
        }
        else {
            ++pager->nr_line_chars;

            if (pager->nr_line_chars > terminal.ws_col) {
                ++pager->nr_lines;
                pager->nr_line_chars = 0;

                if (pager->nr_lines > (terminal.ws_row * PAGING_THRESHOLD)) {
                    should_buffer = false;
                    break;
                }
            }
        }
    }

    if (should_buffer) {
        char* data_copy = (char*) malloc((*length + 1) * sizeof(char));

        if (data_copy == NULL) {
            ERROR_ERRNO(error, errno);
            return true;
        }

        memcpy(data_copy, *data, *length * sizeof(char));
        data_copy[*length] = '\0';
        Array_add(&pager->buffer, (intptr_t) data_copy, error);

        if (ERROR_HAS(error)) {
            free(data_copy);
            return true;
        }

        *data = NULL;
        *length = 0;
        return true;
    }

    return false;
}

static void create_argv(Array* argv, Array* options, Error* error) {
    Array_init(argv, error, EXTERNAL_BINARY, NULL);

    if (ERROR_HAS(error)) {
        return;
    }

    if (options != NULL) {
        Array_extend(argv, options, error);

        if (ERROR_HAS(error)) {
            Array_deinit(argv);
            return;
        }
    }

    Array_add(argv, (intptr_t) NULL, error);

    if (ERROR_HAS(error)) {
        Array_deinit(argv);
        return;
    }

    ERROR_CLEAR(error);
}

static void flush_pager_buffer(Pager* pager, Error* error) {
    int fd = (pager->fd == IO_INVALID_FD) ? STDOUT_FILENO : pager->fd;

    for (size_t i = 0; i < pager->buffer.length; ++i) {
        char* buffer = (char*) pager->buffer.data[i];
        io_write(fd, buffer, strlen(buffer), error);
        free(buffer);

        if (ERROR_HAS(error)) {
            return;
        }
    }

    pager->buffer.length = 0;
}

static void pager_close(intptr_t arg, Error* error) {
    Pager* pager = (Pager*) arg;

    flush_pager_buffer(pager, error);
    Pager_delete(pager);
}

static void pager_write(
        intptr_t arg, char** data, size_t* length, Error* error) {

    Pager* pager = (Pager*) arg;

    if (pager->fd == IO_INVALID_FD) {
        if (buffer_pager_input(pager, data, length, error)) {
            return;
        }

        Array argv;
        create_argv(&argv, pager->options, error);

        if (ERROR_HAS(error)) {
            return;
        }

        int read_write_fds[2];

        if (pipe(read_write_fds) == -1) {
            ERROR_ERRNO(error, errno);
            Array_deinit(&argv);
            return;
        }

        int child_pid = fork();

        if (child_pid == -1) {
            ERROR_ERRNO(error, errno);
            Array_deinit(&argv);
            return;
        }
        else if (child_pid) {
            if (dup2(read_write_fds[0], STDIN_FILENO) == -1) {
                ERROR_ERRNO(error, errno);
                Array_deinit(&argv);
                return;
            }

            close(read_write_fds[0]);
            close(read_write_fds[1]);
            execvp((char*) argv.data[0], (char**) argv.data);
            ERROR_ERRNO(error, errno);
            Array_deinit(&argv);
            return;
        }

        Array_deinit(&argv);
        close(read_write_fds[0]);
        pager->fd = read_write_fds[1];

        flush_pager_buffer(pager, error);
        if (ERROR_HAS(error)) {
            return;
        }
    }

    io_write(pager->fd, *data, *length, error);
    *data = NULL;
    *length = 0;
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
        ERROR_CLEAR(error);
        return;
    }

    if (signal(SIGWINCH, get_terminal_size) == SIG_ERR) {
        ERROR_ERRNO(error, errno);
        return;
    }

    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &terminal) == -1) {
        ERROR_ERRNO(error, errno);
        return;
    }

    Output* output = Output_new(error);

    if (ERROR_HAS(error)) {
        return;
    }

    output->close = pager_close;
    output->write = pager_write;
    output->arg = (intptr_t) Pager_new(options, error);

    if (ERROR_HAS(error)) {
        Output_delete(output);
        return;
    }

    Array_add(outputs, (intptr_t) output, error);

    if (ERROR_HAS(error)) {
        Pager_delete((Pager*) output->arg);
        Output_delete(output);
    }
}

Plugin Pager_Plugin = {
    {NULL},
    get_description,
    get_name,
    run,
};
