// Standard library.
#include <iostream>
#include <string>

// libPurple
#include <purple.h>

// NPAPI
#include <npapi.h>
#include <npfunctions.h>

#include <eon/library/features.h>
#include "main.h"


class Purple {
public:
    static void initialize() {
        purple_debug_set_enabled(true);
    }
};


static NPNetscapeFuncs* browser = NULL;
static NPObject* plugin = NULL;


static bool has_method(NPObject* object, NPIdentifier name) {
    std::string cname = ::browser->utf8fromidentifier(name);
    std::cerr << __func__ << "; name=" << cname << "; error=" << std::endl;
    return false;
}


static bool invoke_default(
    NPObject* object,
    const NPVariant* arguments,
    uint32_t nr_arguments,
    NPVariant* result)
{
    std::cout << __func__ << "; #args=" << nr_arguments << std::endl;
    return false;
}


static bool invoke(
    NPObject* object,
    NPIdentifier name,
    const NPVariant* arguments,
    uint32_t nr_arguments,
    NPVariant* result)
{
    std::string cname = ::browser->utf8fromidentifier(name);
    
    std::cout << __func__ << "; name=" << cname << "; #args=" << nr_arguments
        << std::endl;
    
    ::browser->setexception(object, "Exception during invocation.");
    return false;
}


static bool has_property(NPObject* object, NPIdentifier name) {
    std::string cname = ::browser->utf8fromidentifier(name);
    std::cout << __func__ << "; name=" << cname << std::endl;
    return false;
}


static bool get_property(
    NPObject* object,
    NPIdentifier name,
    NPVariant* result)
{
    std::string cname = ::browser->utf8fromidentifier(name);
    std::cout << __func__ << "; name=" << cname << std::endl;
    return false;
}


static bool set_property(
    NPObject* object,
    NPIdentifier name,
    const NPVariant* value)
{
    std::string cname = ::browser->utf8fromidentifier(name);
    std::cout << __func__ << "; name=" << cname << std::endl;
    return false;
}


static bool remove_property(NPObject* object, NPIdentifier name) {
    std::string cname = ::browser->utf8fromidentifier(name);
    std::cout << __func__ << "; name=" << cname << std::endl;
    return false;
}


static NPClass _plugin_class = {
    NP_CLASS_STRUCT_VERSION,
    NULL,
    NULL,
    NULL,
    has_method,
    invoke,
    invoke_default,
    has_property,
    get_property,
    set_property,
    remove_property,
};


static NPError create(
    NPMIMEType type,
    NPP instance,
    uint16_t mode,
    int16_t nr_arguments,
    char* argn[],
    char* argv[],
    NPSavedData* data)
{
    std::cout << __func__ << "; mode=" << mode << " #args=" << nr_arguments
        << std::endl;
    return NPERR_NO_ERROR;
}


static NPError destroy(NPP instance, NPSavedData** data) {
    std::cout << __func__ << std::endl;
    
    if (::plugin != NULL) {
        ::browser->releaseobject(::plugin);
        
        // TODO: Unset only when the reference count reaches zero?
        ::plugin = NULL;
    }
    
    return NPERR_NO_ERROR;
}


static NPError get_value(NPP instance, NPPVariable what, void* value) {
    std::cout << __func__ << "; what=" << what << " value=" << value
        << std::endl;
    
    if (value == NULL) {
        return NPERR_INVALID_PARAM;
    }
    
    switch (what) {
    case NPPVpluginNameString:
        *reinterpret_cast<const char**>(value) = PLUGIN_NAME;
        break;
    case NPPVpluginDescriptionString:
        *reinterpret_cast<const char**>(value) = PLUGIN_DESCRIPTION;
        break;
    case NPPVpluginScriptableNPObject:
        if (::plugin == NULL) {
            ::plugin = ::browser->createobject(instance, &_plugin_class);
        }
        ::browser->retainobject(::plugin);
        *reinterpret_cast<NPObject**>(value) = ::plugin;
        break;
    default:
        return NPERR_GENERIC_ERROR;
    }
    
    return NPERR_NO_ERROR;
}


static NPError handle_event(NPP instance, void* event) {
    std::cout << __func__ << std::endl;
    return NPERR_NO_ERROR;
}


static NPError set_window(NPP instance, NPWindow* window) {
    std::cout << __func__ << std::endl;
    return NPERR_NO_ERROR;
}


PUBLIC NPError OSCALL NP_GetEntryPoints(NPPluginFuncs* plugin_functions) {
    std::cout << __func__ << std::endl;
    
    if (plugin_functions == NULL) {
        return NPERR_INVALID_FUNCTABLE_ERROR;
    }
    
    plugin_functions->version = (NP_VERSION_MAJOR << 8) | NP_VERSION_MINOR;
    plugin_functions->newp = create;
    plugin_functions->destroy = destroy;
    plugin_functions->getvalue = get_value;
    plugin_functions->event = handle_event;
    plugin_functions->setwindow = set_window;
    
    return NPERR_NO_ERROR;
}


PUBLIC NPError OSCALL NP_Initialize(
    NPNetscapeFuncs* browser_instance
#ifndef _WINDOWS
    , NPPluginFuncs* plugin_functions
#endif
) {
    std::cout << __func__ << std::endl;
    
    if (browser_instance == NULL) {
        return NPERR_INVALID_FUNCTABLE_ERROR;
    }
    if ((browser_instance->version >> 8) > NP_VERSION_MAJOR) {
        return NPERR_INCOMPATIBLE_VERSION_ERROR;
    }
    
    ::browser = browser_instance;
    Purple::initialize();
    
#ifndef _WINDOWS
    NP_GetEntryPoints(plugin_functions);
#endif
    
    return NPERR_NO_ERROR;
}


PUBLIC NPError OSCALL NP_Shutdown() {
    std::cout << __func__ << std::endl;
    ::browser = NULL;
    
    return NPERR_NO_ERROR;
}


PUBLIC char* NP_GetMIMEDescription() {
    std::cout << __func__ << std::endl;
    
    // <MIME Type>:<extension>:<description>
    return const_cast<char*>(PLUGIN_MIME_TYPE ": : ");
}


PUBLIC NPError OSCALL NP_GetValue(
    void* instance,
    NPPVariable what,
    void* value)
{
    return get_value(reinterpret_cast<NPP>(instance), what, value);
}
