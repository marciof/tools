#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include "../Array.h"
#include "../io.h"
#include "Less_Plugin.h"

#define EXTERNAL_BINARY "less"
#define PAGING_THRESHOLD 0.5

typedef struct {
    bool has_buffer_timer;
    pthread_t buffer_timer;
    Error buffer_timer_error;
    Array buffers;
    Array* options;
    size_t nr_lines;
    size_t nr_line_chars;
    int fd;
} Pager;

static struct winsize terminal;

static void get_terminal_size(int num) {
    signal(SIGWINCH, get_terminal_size);
    ioctl(STDOUT_FILENO, TIOCGWINSZ, &terminal);
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

    Array_add(argv, argv->length, (intptr_t) NULL, error);

    if (ERROR_HAS(error)) {
        Array_deinit(argv);
        return;
    }

    ERROR_CLEAR(error);
}

static void flush_pager_buffer(Pager* pager, Error* error) {
    for (size_t i = 0; i < pager->buffers.length; ++i) {
        Buffer* buffer = (Buffer*) pager->buffers.data[i];

        io_write(pager->fd, buffer, error);
        Buffer_delete(buffer);

        if (ERROR_HAS(error)) {
            return;
        }
    }

    pager->buffers.length = 0;
    ERROR_CLEAR(error);
}

void* flush_pager_buffer_timer(void* arg) {
    Pager* pager = (Pager*) arg;
    struct timeval timeout;

    timeout.tv_sec = 0;
    timeout.tv_usec = 500 * 1000;

    if (select(0, NULL, NULL, NULL, &timeout) == -1) {
        ERROR_ERRNO(&pager->buffer_timer_error, errno);
    }
    else {
        pager->fd = STDOUT_FILENO;
        flush_pager_buffer(pager, &pager->buffer_timer_error);
    }

    return NULL;
}

static bool buffer_pager_input(Pager* pager, Buffer** buffer, Error* error) {
    bool should_buffer = true;

    for (size_t i = 0; i < (*buffer)->length; ++i) {
        if ((*buffer)->data[i] == '\n') {
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

    if (!should_buffer) {
        ERROR_CLEAR(error);
        return false;
    }

    Array_add(
        &pager->buffers, pager->buffers.length, (intptr_t) *buffer, error);

    if (ERROR_HAS(error)) {
        return true;
    }

    if (!pager->has_buffer_timer) {
        int error_nr = pthread_create(
            &pager->buffer_timer, NULL, flush_pager_buffer_timer, pager);

        if (error_nr) {
            ERROR_ERRNO(error, error_nr);
            return true;
        }

        pager->has_buffer_timer = true;
    }

    *buffer = NULL;
    ERROR_CLEAR(error);
    return true;
}

static void Pager_delete(Pager* pager, Error* error) {
    if (pager->has_buffer_timer) {
        if (ERROR_HAS(&pager->buffer_timer_error)) {
            *error = pager->buffer_timer_error;
            return;
        }

        int error_nr = pthread_cancel(pager->buffer_timer);

        if (error_nr && (error_nr != ESRCH)) {
            ERROR_ERRNO(error, error_nr);
            return;
        }

        error_nr = pthread_join(pager->buffer_timer, NULL);

        if (error_nr) {
            ERROR_ERRNO(error, error_nr);
            return;
        }
    }

    for (size_t i = 0; i < pager->buffers.length; ++i) {
        Buffer_delete((Buffer*) pager->buffers.data[i]);
    }

    Array_deinit(&pager->buffers);
    free(pager);
}

static Pager* Pager_new(Array* options, Error* error) {
    Pager* pager = (Pager*) malloc(sizeof(*pager));

    if (pager == NULL) {
        ERROR_ERRNO(error, errno);
        return NULL;
    }

    pager->has_buffer_timer = false;
    pager->options = options;
    pager->nr_lines = 0;
    pager->nr_line_chars = 0;
    pager->fd = IO_INVALID_FD;

    ERROR_CLEAR(&pager->buffer_timer_error);
    Array_init(&pager->buffers, error, NULL);

    if (ERROR_HAS(error)) {
        free(pager);
        return NULL;
    }

    ERROR_CLEAR(error);
    return pager;
}

static void Output_close(Output* output, Error* error) {
    Pager* pager = (Pager*) output->arg;

    if (pager->fd == IO_INVALID_FD) {
        pager->fd = STDOUT_FILENO;
    }

    flush_pager_buffer(pager, error);

    if (!ERROR_HAS(error)) {
        Pager_delete(pager, error);
    }
}

static void Output_write(Output* output, Buffer** buffer, Error* error) {
    Pager* pager = (Pager*) output->arg;

    if (pager->fd == IO_INVALID_FD) {
        if (buffer_pager_input(pager, buffer, error)) {
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

    io_write(pager->fd, *buffer, error);
    (*buffer)->length = 0;
}

static const char* Plugin_get_description() {
    return "page output if needed via `" EXTERNAL_BINARY "`";
}

static const char* Plugin_get_name() {
    return EXTERNAL_BINARY;
}

static void Plugin_run(
        Plugin* plugin, Array* inputs, Array* outputs, Error* error) {

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

    output->close = Output_close;
    output->write = Output_write;
    output->arg = (intptr_t) Pager_new(&plugin->options, error);

    if (ERROR_HAS(error)) {
        Output_delete(output);
        return;
    }

    Array_add(outputs, outputs->length, (intptr_t) output, error);

    if (ERROR_HAS(error)) {
        Output_delete(output);
    }
    else {
        ERROR_CLEAR(error);
    }
}

Plugin Pager_Plugin = {
    {NULL},
    Plugin_get_description,
    Plugin_get_name,
    Plugin_run,
};
