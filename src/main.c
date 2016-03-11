#include <stddef.h>
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


static void cleanup(Array resources, Error error) {
    if (error) {
        fprintf(stderr, "%s\n", error);
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


int main(int argc, char* argv[]) {
    Error error;
    Array resources = Options_parse(
        argc, argv, plugins, STATIC_ARRAY_LENGTH(plugins), &error);

    if (resources == NULL) {
        cleanup(NULL, error ? error : NULL);
        return EXIT_SUCCESS;
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i] != NULL) {
            plugins[i]->run(resources, plugins[i]->options, &error);

            if (error) {
                fprintf(stderr, "%s: %s\n", plugins[i]->get_name(), error);
                cleanup(resources, NULL);
                return EXIT_FAILURE;
            }
        }
    }

    for (size_t i = 0; i < resources->length; ++i) {
        Resource resource = (Resource) resources->data[i];

        if (resource == NULL) {
            continue;
        }

        int fd = resource->fd;

        if (fd != RESOURCE_NO_FD) {
            ssize_t nr_bytes_read;
            const int BUFFER_SIZE = 256;
            char buffer[BUFFER_SIZE];

            while ((nr_bytes_read = read(fd, buffer, BUFFER_SIZE - 1)) > 0) {
                buffer[nr_bytes_read] = '\0';
                fputs(buffer, stdout);
            }

            close(fd);
        }
    }

    cleanup(resources, NULL);
    return EXIT_SUCCESS;
}
