#include "../list/Linked_List.h"
#include "../list/List.h"
#include "../types.h"
#include "stdlib.h"


typedef struct _Listener* Listener;

struct _Listener {
    void (*function)(ptr_t argument);
    ptr_t argument;
};


static bool has_registered = false;
static List listeners = NULL;


/**
 * Calls registered functions.
 */
static void call_listeners(void) {
    if (has_registered && (listeners != NULL)) {
        while (List_length(listeners) > 0) {
            Listener listener = (Listener) List_remove(listeners, 0).data;
            
            listener->function(listener->argument);
            free(listener);
        }
        
        List_delete(listeners);
    }
}


void atexit_ext(void (*function)(ptr_t argument), ptr_t argument) {
    Listener listener;
    
    if (!has_registered) {
        if (atexit(call_listeners) != 0) {
            errno = ENOMEM;
            return;
        }
        
        has_registered = true;
    }
    
    if (listeners == NULL) {
        listeners = List_new(Linked_List);
        
        if (listeners == NULL) {
            errno = ENOMEM;
            return;
        }
    }
    
    listener = (Listener) malloc(sizeof(struct _Listener));
    
    if (listener == NULL) {
        errno = ENOMEM;
        return;
    }
    
    List_insert(listeners, DATA(listener), 0);
    
    if (errno == ENOMEM) {
        free(listener);
        errno = ENOMEM;
        return;
    }
    
    listener->function = function;
    listener->argument = argument;
    errno = ENONE;
}
