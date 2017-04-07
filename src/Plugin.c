#include <stdlib.h>
#include "Plugin.h"

void Output_delete(struct Output* output) {
    free(output);
}

struct Output* Output_new(struct Plugin* plugin, Error* error) {
    struct Output* output = (struct Output*) malloc(sizeof(*output));

    if (output == NULL) {
        Error_add_errno(error, errno);
        return NULL;
    }

    output->plugin = plugin;
    return output;
}
