#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include "Plugin.h"

void Resource_delete(Resource* resource) {
    if (resource != NULL) {
        memset(resource, 0, sizeof(*resource));
        free(resource);
    }
}

Resource* Resource_new(char* name, int fd, Error* error) {
    Resource* resource = (Resource*) malloc(sizeof(*resource));

    if (resource == NULL) {
        Error_errno(error, errno);
        return NULL;
    }

    resource->name = name;
    resource->fd = fd;

    return resource;
}
