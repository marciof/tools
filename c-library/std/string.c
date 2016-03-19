#include "../util.h"
#include "stdio.h"
#include "stdlib.h"
#include "string.h"


#if C_STANDARD >= 199901L
    #define HAVE_VSNPRINTF 1
#else
    #define HAVE_VSNPRINTF 0
#endif


WARN_DEPRECATION_DISABLE


char* strcopy(const char* string) {
    return strncopy(string, strlen(string));
}


char* strformat(const char* format, ...) {
    va_list args;
    char* string;
    int error;
    
    va_start(args, format);
    string = strvformat(format, args);
    error = errno;
    va_end(args);
    
    errno = error;
    return string;
}


char* strjoin(size_t length, const char** strings, const char* separator) {
    size_t i, string_length = 0;
    char* string;
    char* s;
    
    if (length == 0) {
        return strcopy("");
    }
    
    for (i = 0; i < (length - 1); ++i) {
        string_length += strlen(strings[i]) + strlen(separator);
    }
    
    string_length += strlen(strings[length - 1]);
    s = string = (char*) malloc((string_length + 1) * sizeof(char));
    
    if (string == NULL) {
        errno = ENOMEM;
        return NULL;
    }
    
    for (i = 0; i < (length - 1); ++i) {
        s += sprintf(s, "%s%s", strings[i], separator);
    }
    
    strcpy(s, strings[length - 1]);
    errno = ENONE;
    return string;
}


char* strncopy(const char* string, size_t length) {
    char* copy = (char*) malloc((length + 1) * sizeof(char));
    
    if (copy == NULL) {
        errno = ENOMEM;
        return NULL;
    }
    
    strncpy(copy, string, length);
    copy[length] = '\0';
    errno = ENONE;
    return copy;
}


bool strprefix(const char* string, const char* prefix) {
    errno = ENONE;
    
    while ((*string != '\0') && (*prefix != '\0')) {
        if (*string++ != *prefix++) {
            return false;
        }
    }
    
    return (*prefix == '\0') ? true : false;
}


char** strsplit(const char* string, const char* separator, size_t* length) {
    size_t separator_length = strlen(separator);
    size_t tokens_length = 0;
    char** tokens = (char**) malloc((strlen(string) + 1) * sizeof(char*));
    char* start_offset = (char*) string;
    char* end_offset;
    
    if (tokens == NULL) {
        errno = ENOMEM;
        return NULL;
    }
    
    /* Find all tokens until the end of the string. */
    do {
        end_offset = (separator_length == 0) ?
            (*start_offset == '\0' ? NULL : (start_offset + 1)) :
            strstr(start_offset, separator);
        
        /* Skip empty tokens. */
        if ((start_offset != end_offset) && (*start_offset != '\0')) {
            char* token = (end_offset == NULL) ?
                strcopy(start_offset) :
                strncopy(start_offset, (size_t) (end_offset - start_offset));
            
            if (token == NULL) {
                /* Rollback. */
                size_t i;
                
                for (i = 0; i < tokens_length; ++i) {
                    free(tokens[i]);
                }
                
                free(tokens);
                errno = ENOMEM;
                return NULL;
            }
            
            tokens[tokens_length++] = token;
        }
        
        start_offset = end_offset + separator_length;
    }
    while (end_offset != NULL);
    
    if (length != NULL) {
        *length = tokens_length;
    }
    
    tokens[tokens_length] = NULL;
    errno = ENONE;
    return tokens;
}


bool strsuffix(const char* string, const char* suffix) {
    if (suffix[0] == '\0') {
        errno = ENONE;
        return true;
    }
    else {
        /* Needs cast since some implementations return (const char*). */
        char* match = (char*) strstr(string, suffix);
        size_t length;
        
        if (match == NULL) {
            errno = ENONE;
            return false;
        }
        
        for (length = 0; *suffix != '\0'; ++suffix, ++length) {
        }
        
        errno = ENONE;
        return match[length] == '\0' ? true : false;
    }
}


char* strvformat(const char* format, va_list arguments) {
#if HAVE_VSNPRINTF
    long length = BUFSIZ;
    char* string = NULL;
    
    while (true) {
        char* temp = (char*) realloc(string, length * sizeof(char));
        va_list args_copy;
        int count;
        
        if (temp == NULL) {
            free(string);
            errno = ENOMEM;
            return NULL;
        }
        
        va_copy(args_copy, arguments);
        string = temp;
        count = vsnprintf(string, length, format, args_copy);
        va_end(args_copy);
        
        if ((count < 0) || (count == length) || (count == (length - 1))) {
            /* Truncated without indication of how big it needs to be. */
            length *= 2;
        }
        else if (count > length) {
            /* Add one character for NUL and another to prevent ambiguities. */
            length = count + 1 + 1;
        }
        else {
            string[count] = '\0';
            errno = ENONE;
            return string;
        }
    }
#else
    va_list original_args;
    int length;
    
    va_copy(original_args, arguments);
    length = vfprintf(stdnull, format, arguments);
    
    if (length < 0) {
        va_end(original_args);
        errno = ENOMEM;
        return NULL;
    }
    else {
        char* string = (char*) malloc((length + 1) * sizeof(char));
        
        if (string == NULL) {
            va_end(original_args);
            errno = ENOMEM;
            return NULL;
        }
        
        if (vsprintf(string, format, original_args) != length) {
            va_end(original_args);
            free(string);
            errno = ENOMEM;
            return NULL;
        }
        
        va_end(original_args);
        errno = ENONE;
        return string;
    }
#endif
}
