#pragma once
#include <stddef.h>
#include "../Array.h"
#include "../Error.h"


#define RESOURCE_NO_FD ((int) -1)


typedef struct {
    char* name;
    int fd;
}* Resource;


typedef struct {
    Array options;
    const char* (*get_description)();
    const char* (*get_name)();
    void (*run)(Array inputs, Array options, int* output_fd, Error* error);
} Plugin;


void Resource_delete(Resource resource);
Resource Resource_new(char* name, int fd, Error* error);
