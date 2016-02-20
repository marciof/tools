#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include "string.h"


char* strcopy(const char* string, char** error) {
    return strncopy(string, strlen(string), error);
}


char* strformat(const char* format, char** error, ...) {
    va_list args;

    va_start(args, error);
    char* string = strvformat(format, args, error);
    va_end(args);
    
    return string;
}


char* strjoin(
        size_t length,
        const char** strings,
        const char* separator,
        char** error) {

    if (length == 0) {
        return strcopy("", error);
    }

    size_t string_length = 0;

    for (size_t i = 0; i < (length - 1); ++i) {
        string_length += strlen(strings[i]) + strlen(separator);
    }

    char* string;
    char* s;

    string_length += strlen(strings[length - 1]);
    s = string = (char*) malloc((string_length + 1) * sizeof(char));
    
    if (string == NULL) {
        *error = strerror(ENOMEM);
        return NULL;
    }
    
    for (size_t i = 0; i < (length - 1); ++i) {
        s += sprintf(s, "%s%s", strings[i], separator);
    }
    
    strcpy(s, strings[length - 1]);
    *error = NULL;
    return string;
}


char* strncopy(const char* string, size_t length, char** error) {
    char* copy = (char*) malloc((length + 1) * sizeof(char));
    
    if (copy == NULL) {
        *error = strerror(ENOMEM);
        return NULL;
    }
    
    strncpy(copy, string, length);
    copy[length] = '\0';
    *error = NULL;
    return copy;
}


bool strprefix(const char* string, const char* prefix) {
    while ((*string != '\0') && (*prefix != '\0')) {
        if (*string++ != *prefix++) {
            return false;
        }
    }
    
    return *prefix == '\0';
}


char** strsplit(
        const char* string,
        const char* separator,
        size_t* length,
        char** error) {

    size_t separator_length = strlen(separator);
    size_t tokens_length = 0;
    char** tokens = (char**) malloc((strlen(string) + 1) * sizeof(char*));
    char* start_offset = (char*) string;
    char* end_offset;
    
    if (tokens == NULL) {
        *error = strerror(ENOMEM);
        return NULL;
    }
    
    // Find all tokens until the end of the string.
    do {
        end_offset = (separator_length == 0)
            ? (*start_offset == '\0' ? NULL : (start_offset + 1))
            : strstr(start_offset, separator);
        
        // Skip empty tokens.
        if ((start_offset != end_offset) && (*start_offset != '\0')) {
            char* token = (end_offset == NULL)
                ? strcopy(start_offset, error)
                : strncopy(
                    start_offset, (size_t) (end_offset - start_offset), error);
            
            if (*error) {
                // Rollback.
                for (size_t i = 0; i < tokens_length; ++i) {
                    free(tokens[i]);
                }
                
                free(tokens);
                *error = strerror(ENOMEM);
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
    *error = NULL;
    return tokens;
}


bool strsuffix(const char* string, const char* suffix) {
    if (suffix[0] == '\0') {
        return true;
    }

    const char* match = strstr(string, suffix);

    if (match == NULL) {
        return false;
    }

    size_t length;
    for (length = 0; *suffix != '\0'; ++suffix, ++length);
    return match[length] == '\0';
}


char* strvformat(const char* format, va_list arguments, char** error) {
    long length = BUFSIZ;
    char* string = NULL;

    while (true) {
        char* temp = (char*) realloc(string, length * sizeof(char));
        va_list args_copy;

        if (temp == NULL) {
            free(string);
            *error = strerror(ENOMEM);
            return NULL;
        }

        va_copy(args_copy, arguments);
        string = temp;
        int count = vsnprintf(string, length, format, args_copy);
        va_end(args_copy);

        if ((count < 0) || (count == length) || (count == (length - 1))) {
            // Truncated without indication of how big it needs to be.
            length *= 2;
        }
        else if (count > length) {
            // Add one character for NUL and another to prevent ambiguities.
            length = count + 1 + 1;
        }
        else {
            string[count] = '\0';
            *error = NULL;
            return string;
        }
    }
}
