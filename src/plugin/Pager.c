#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include "../Array.h"
#include "../io.h"
#include "../popen2.h"
#include "Pager.h"

// Don't use `pager` as it's not available in all systems.
#define EXTERNAL_BINARY "less"

#define PAGING_THRESHOLD 0.6

typedef struct {
    bool has_timer;
    Error timer_error;
    pthread_t timer_thread;
    pthread_mutex_t timer_mutex;
    Array buffers;
    Array* options;
    size_t nr_lines;
    size_t nr_line_chars;
    // Set to `IO_NULL_FD` until the pager starts (if at all).
    int fd;
    pid_t child_pid;
} Pager;

static struct winsize terminal;

// FIXME: check `errno`
static void get_terminal_size(int signal_nr) {
    signal(SIGWINCH, get_terminal_size);
    ioctl(STDOUT_FILENO, TIOCGWINSZ, &terminal);
}

static void init_argv(Array* argv, Array* options, Error* error) {
    Array_init(argv, error, EXTERNAL_BINARY, NULL);

    if (ERROR_HAS(error)) {
        return;
    }

    if (!ARRAY_IS_NULL_INITIALIZED(options)) {
        Array_extend(argv, options, error);

        if (ERROR_HAS(error)) {
            Array_deinit(argv);
            return;
        }
    }

    Array_add(argv, argv->length, (intptr_t) NULL, error);

    if (ERROR_HAS(error)) {
        Array_deinit(argv);
    }
}

static void protect_buffer(Pager* pager, bool do_lock, Error* error) {
    if (pager->has_timer) {
        int error_nr = (do_lock ? pthread_mutex_lock : pthread_mutex_unlock)
            (&pager->timer_mutex);

        if (error_nr) {
            Error_add(error, strerror(error_nr));
        }
    }
}

static void flush_buffer(Pager* pager, int default_fd, Error* error) {
    protect_buffer(pager, true, error);

    if (ERROR_HAS(error)) {
        return;
    }

    if (pager->fd == IO_NULL_FD) {
        pager->fd = default_fd;
    }

    for (size_t i = 0; i < pager->buffers.length; ++i) {
        Buffer* buffer = (Buffer*) pager->buffers.data[i];

        io_write(
            pager->fd,
            (uint8_t*) buffer->data,
            buffer->length * sizeof(buffer->data[0]),
            error);

        Buffer_delete(buffer);

        if (ERROR_HAS(error)) {
            pager->buffers.data[i] = (intptr_t) NULL;
            return;
        }
    }

    pager->buffers.length = 0;
    protect_buffer(pager, false, error);
}

void* flush_buffer_timer(void* arg) {
    Pager* pager = (Pager*) arg;
    struct timeval timeout;

    timeout.tv_sec = 0;
    timeout.tv_usec = 500 * 1000;

    if (select(0, NULL, NULL, NULL, &timeout) == -1) {
        Error_add(&pager->timer_error, strerror(errno));
    }
    else {
        flush_buffer(pager, STDOUT_FILENO, &pager->timer_error);
    }

    return NULL;
}

static bool buffer_input(Pager* pager, Buffer** buffer, Error* error) {
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
        return false;
    }

    protect_buffer(pager, true, error);

    if (ERROR_HAS(error)) {
        return false;
    }

    Array_add(
        &pager->buffers, pager->buffers.length, (intptr_t) *buffer, error);

    if (ERROR_HAS(error)) {
        return false;
    }

    protect_buffer(pager, false, error);

    if (ERROR_HAS(error)) {
        return false;
    }

    if (!pager->has_timer) {
        int error_nr = pthread_create(
            &pager->timer_thread, NULL, flush_buffer_timer, pager);

        if (error_nr) {
            Error_add(error, strerror(error_nr));
            return false;
        }

        error_nr = pthread_mutex_init(&pager->timer_mutex, NULL);

        // FIXME: stop thread?
        if (error_nr) {
            Error_add(error, strerror(error_nr));
            return false;
        }

        pager->has_timer = true;
    }

    *buffer = NULL;
    return true;
}

static void Pager_delete(Pager* pager, Error* error) {
    if (pager->has_timer) {
        if (ERROR_HAS(&pager->timer_error)) {
            // FIXME: don't discard errors
            Error_copy(error, &pager->timer_error);
            return;
        }

        int error_nr = pthread_cancel(pager->timer_thread);

        if (error_nr && (error_nr != ESRCH)) {
            Error_add(error, strerror(error_nr));
            return;
        }

        error_nr = pthread_join(pager->timer_thread, NULL);

        if (error_nr) {
            Error_add(error, strerror(error_nr));
            return;
        }

        error_nr = pthread_mutex_destroy(&pager->timer_mutex);

        if (error_nr) {
            Error_add(error, strerror(error_nr));
            return;
        }
    }

    for (size_t i = 0; i < pager->buffers.length; ++i) {
        Buffer_delete((Buffer*) pager->buffers.data[i]);
    }

    Array_deinit(&pager->buffers);

    if ((pager->fd != IO_NULL_FD) && (close(pager->fd) == -1)) {
        Error_add(error, strerror(errno));
        return;
    }

    if (pager->child_pid != -1) {
        int status = wait_subprocess(pager->child_pid, error);

        if (ERROR_HAS(error) || (status != 0)) {
            Error_add(error, "`" EXTERNAL_BINARY "`");
            return;
        }
    }

    free(pager);
}

static Pager* Pager_new(Array* options, Error* error) {
    Pager* pager = (Pager*) malloc(sizeof(*pager));

    if (pager == NULL) {
        Error_add(error, strerror(errno));
        return NULL;
    }

    Array_init(&pager->buffers, error, NULL);

    if (ERROR_HAS(error)) {
        free(pager);
        return NULL;
    }

    pager->has_timer = false;
    pager->options = options;
    pager->nr_lines = 0;
    pager->nr_line_chars = 0;
    pager->fd = IO_NULL_FD;
    pager->child_pid = -1;

    ERROR_CLEAR(&pager->timer_error);
    return pager;
}

static void Output_close(Output* output, Error* error) {
    Pager* pager = (Pager*) output->arg;
    flush_buffer(pager, STDOUT_FILENO, error);
    Pager_delete(pager, error);
}

static void Output_write(Output* output, Buffer** buffer, Error* error) {
    Pager* pager = (Pager*) output->arg;

    if (pager->fd == IO_NULL_FD) {
        if (buffer_input(pager, buffer, error)) {
            return;
        }

        Array argv;
        init_argv(&argv, pager->options, error);

        if (ERROR_HAS(error)) {
            return;
        }

        int fd = popen2(
            (char*) argv.data[0],
            (char**) argv.data,
            false,
            IO_NULL_FD,
            IO_NULL_FD,
            &pager->child_pid,
            error);

        if (ERROR_HAS(error)) {
            Error_add(error, strerror(errno));
            Error_add(error, "`" EXTERNAL_BINARY "`");
            Array_deinit(&argv);
            return;
        }

        Array_deinit(&argv);
        flush_buffer(pager, fd, error);

        if (ERROR_HAS(error)) {
            return;
        }
    }

    io_write(
        pager->fd,
        (uint8_t*) (*buffer)->data,
        (*buffer)->length * sizeof((*buffer)->data[0]),
        error);

    (*buffer)->length = 0;
}

static const char* Plugin_get_description() {
    return "page output via `" EXTERNAL_BINARY "` when needed";
}

static const char* Plugin_get_name() {
    return "pager";
}

static bool Plugin_is_available(Error* error) {
    return popen2_can_run(EXTERNAL_BINARY, error);
}

static void Plugin_run(
        Plugin* plugin, Array* inputs, Array* outputs, Error* error) {

    bool is_tty = io_is_tty(STDOUT_FILENO, error);

    if (ERROR_HAS(error) || !is_tty) {
        return;
    }

    // FIXME: convert fatal error to warning
    if (signal(SIGWINCH, get_terminal_size) == SIG_ERR) {
        Error_add(error, strerror(errno));
        return;
    }

    // FIXME: cleanup signal handler
    // FIXME: convert fatal error to warning
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &terminal) == -1) {
        Error_add(error, strerror(errno));
        return;
    }

    Output* output = Output_new(plugin, error);

    // FIXME: cleanup signal handler
    if (ERROR_HAS(error)) {
        return;
    }

    output->close = Output_close;
    output->write = Output_write;
    output->arg = (intptr_t) Pager_new(&plugin->options, error);

    // FIXME: cleanup signal handler
    if (ERROR_HAS(error)) {
        Output_delete(output);
        return;
    }

    Array_add(outputs, outputs->length, (intptr_t) output, error);

    // FIXME: cleanup signal handler
    if (ERROR_HAS(error)) {
        Pager_delete((Pager*) output->arg, error);
        Output_delete(output);
    }
}

Plugin Pager_Plugin = {
    ARRAY_NULL_INITIALIZER,
    Plugin_get_description,
    Plugin_get_name,
    Plugin_is_available,
    Plugin_run,
};
