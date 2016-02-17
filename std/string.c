#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include "string.h"


char* strncopy(const char* string, size_t length) {
    char* copy = (char*) malloc((length + 1) * sizeof(char));

    if (copy == NULL) {
        errno = ENOMEM;
        return NULL;
    }

    strncpy(copy, string, length);
    copy[length] = '\0';

    errno = 0;
    return copy;
}
