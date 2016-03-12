#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "Array.h"
#include "Options.h"
#include "plugin/File_Plugin.h"
#include "plugin/Ls_Plugin.h"
#include "plugin/Pipe_Plugin.h"


static Plugin* plugins[] = {
    &Pipe_Plugin,
    &File_Plugin,
    &Ls_Plugin,
};


static void cleanup(Array resources, Error* error) {
    if (error != NULL) {
        fprintf(stderr, "%s\n", *error);
    }

    if (resources != NULL) {
        for (size_t i = 0; i < resources->length; ++i) {
            Resource_delete((Resource) resources->data[i]);
        }

        Array_delete(resources);
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i] != NULL) {
            Array_delete(plugins[i]->options);
            plugins[i] = NULL;
        }
    }
}


static void flush_input(int input_fd, int output_fd, Error* error) {
    ssize_t bytes_read;
    const int BUFFER_SIZE = 4 * 1024;
    uint8_t buffer[BUFFER_SIZE];

    while ((bytes_read = read(input_fd, buffer, BUFFER_SIZE)) > 0) {
        uint8_t* next_write = buffer;

        while (bytes_read > 0) {
            ssize_t bytes_written = write(
                output_fd, next_write, (size_t) bytes_read);

            if (bytes_written == -1) {
                Error_errno(error, errno);
                return;
            }

            bytes_read -= bytes_written;
            next_write += bytes_written;
        }
    }

    if ((errno == 0) || (errno == EIO) || (errno == ENOTTY)) {
        Error_clear(error);
    }
    else {
        Error_errno(error, errno);
    }
}


int main(int argc, char* argv[]) {
    Error error;
    int output_fd = STDOUT_FILENO;

    Array inputs = Options_parse(
        argc, argv, plugins, STATIC_ARRAY_LENGTH(plugins), &error);

    if (inputs == NULL) {
        cleanup(NULL, error ? &error : NULL);
        return EXIT_SUCCESS;
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i] != NULL) {
            plugins[i]->run(inputs, plugins[i]->options, &output_fd, &error);

            if (error) {
                fprintf(stderr, "%s: %s\n", plugins[i]->get_name(), error);
                cleanup(inputs, NULL);
                return EXIT_FAILURE;
            }
        }
    }

    for (size_t i = 0; i < inputs->length; ++i) {
        Resource input = (Resource) inputs->data[i];

        if (input != NULL) {
            int input_fd = input->fd;

            if (input_fd != RESOURCE_NO_FD) {
                flush_input(input_fd, output_fd, &error);
                close(input_fd);

                if (Error_has(&error)) {
                    cleanup(inputs, &error);
                    return EXIT_FAILURE;
                }
            }
        }
    }

    cleanup(inputs, NULL);
    return EXIT_SUCCESS;
}
