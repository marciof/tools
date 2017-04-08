#include <stdlib.h>
#include "Buffer.h"

void Buffer_delete(struct Buffer* buffer) {
    free(buffer);
}

struct Buffer* Buffer_new(size_t max_length, struct Error* error) {
    struct Buffer* buffer = (struct Buffer*) malloc(
        offsetof(struct Buffer, data) + sizeof(buffer->data[0]) * max_length);

    if (buffer == NULL) {
        Error_add_errno(error, errno);
        return NULL;
    }

    buffer->length = 0;
    return buffer;
}
