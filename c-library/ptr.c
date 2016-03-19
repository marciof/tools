#include "ptr.h"


const ptr_t null = {0};


ptr_t __wrap_code_pointer(void (*code)()) {
    ptr_t p = null;
    
    p.code = code;
    return p;
}


ptr_t __wrap_data_pointer(void* data) {
    ptr_t p = null;
    
    p.data = data;
    return p;
}
