#pragma once
#include <stdbool.h>
#include <string.h>

typedef const char* Error;

#define ERROR_UNSPECIFIED ((Error) "")

#define /* void */ ERROR_CLEAR(/* Error* */ error) \
    (*(error) = NULL)

#define /* void */ ERROR_ERRNO(/* Error* */ error, /* int */ code) \
    ERROR_SET((error), strerror(code))

#define /* bool */ ERROR_HAS(/* Error* */ error) \
    (*(error) != NULL)

#define /* void */ ERROR_SET(/* Error* */ error, /* char* */ message) \
    (*(error) = message)
