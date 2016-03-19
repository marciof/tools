#include "../util.h"
#include "errno.h"
#include "stdio.h"
#include "stdlib.h"


#ifdef _WIN32
#   define NULL_FILE_NAME "nul"
#else
#   define NULL_FILE_NAME "/dev/null"
#endif


WARN_DEPRECATION_DISABLE


static void close_stream(ptr_t stream) {
    fclose((FILE*) stream.data);
}


/**
 * @internal
 *
 * Gets the standard null stream location.
 *
 * @return standard null stream location
 */
FILE** __stdnull_location(void) {
    static FILE* stream = NULL;
    
    if (stream == NULL) {
        int error = errno;
        
        stream = fopen(NULL_FILE_NAME, "r+");
        atexit_ext(close_stream, DATA(stream));
        errno = error;
    }
    
    return &stream;
}
