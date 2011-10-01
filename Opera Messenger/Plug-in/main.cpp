#include <iostream>
#include <string>

#include <npapi.h>
#include <npfunctions.h>
#include <npruntime.h>
#include <nptypes.h>

#include "main.h"


static NPNetscapeFuncs* _browser = NULL;
static NPObject* _plugin = NULL;


static bool has_method(NPObject* object, NPIdentifier name) {
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
    return cname == "test";
}


static bool invoke_default(
    NPObject* object,
    const NPVariant* arguments,
    uint32_t nr_arguments,
    NPVariant* result)
{
    std::cout << __func__ << ": #args=" << nr_arguments << std::endl;
    INT32_TO_NPVARIANT(12345, *result);
    return true;
}


static bool invoke(
    NPObject* object,
    NPIdentifier name,
    const NPVariant* arguments,
    uint32_t nr_arguments,
    NPVariant* result)
{
    std::string cname = _browser->utf8fromidentifier(name);
    
    std::cout << __func__ << ": name=" << cname
        << " #args=" << nr_arguments << std::endl;
    
    if (cname == "test") {
        return invoke_default(object, arguments, nr_arguments, result);
    }
    else {
        _browser->setexception(object, "Exception during invocation.");
        return false;
    }
}


static bool has_property(NPObject* object, NPIdentifier name) {
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
    return false;
}


static bool get_property(
    NPObject* object,
    NPIdentifier name,
    NPVariant* result)
{
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
    return false;
}


static bool set_property(
    NPObject* object,
    NPIdentifier name,
    const NPVariant* value)
{
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
    return false;
}


static bool remove_property(NPObject* object, NPIdentifier name) {
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
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
    std::cout << __func__ << ": mode=" << mode
        << " #args=" << nr_arguments << std::endl;
    return NPERR_NO_ERROR;
}


static NPError destroy(NPP instance, NPSavedData** data) {
    std::cout << __func__ << std::endl;
    
    if (_plugin != NULL) {
        _browser->releaseobject(_plugin);
        _plugin = NULL;
    }
    
    return NPERR_NO_ERROR;
}


static NPError get_value(NPP instance, NPPVariable what, void* value) {
    std::cout << __func__ << ": what=" << what
        << " value=" << value << std::endl;
    
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
        if (_plugin == NULL) {
            _plugin = _browser->createobject(instance, &_plugin_class);
        }
        _browser->retainobject(_plugin);
        *reinterpret_cast<NPObject**>(value) = _plugin;
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


extern "C" NPError OSCALL NP_GetEntryPoints(NPPluginFuncs* plugin) {
    std::cout << __func__ << std::endl;
    
    if (plugin == NULL) {
        return NPERR_INVALID_FUNCTABLE_ERROR;
    }
    
    plugin->version = (NP_VERSION_MAJOR << 8) | NP_VERSION_MINOR;
    plugin->newp = create;
    plugin->destroy = destroy;
    plugin->getvalue = get_value;
    plugin->event = handle_event;
    plugin->setwindow = set_window;
    
    return NPERR_NO_ERROR;
}


extern "C" NPError OSCALL NP_Initialize(NPNetscapeFuncs* browser
#ifndef _WINDOWS
    , NPPluginFuncs* plugin
#endif
) {
    std::cout << __func__ << std::endl;
    
    if (browser == NULL) {
        return NPERR_INVALID_FUNCTABLE_ERROR;
    }
    if ((browser->version >> 8) > NP_VERSION_MAJOR) {
        return NPERR_INCOMPATIBLE_VERSION_ERROR;
    }
    
    _browser = browser;
    
#ifndef _WINDOWS
    NP_GetEntryPoints(plugin);
#endif
    
    return NPERR_NO_ERROR;
}


extern "C" NPError OSCALL NP_Shutdown() {
    std::cout << __func__ << std::endl;
    _browser = NULL;
    return NPERR_NO_ERROR;
}


extern "C" char* NP_GetMIMEDescription() {
    std::cout << __func__ << std::endl;
    
    // <MIME Type>:<extension>:<description>
    return const_cast<char*>(PLUGIN_MIME_TYPE ": : ");
}


extern "C" NPError OSCALL NP_GetValue(
    void* instance,
    NPPVariable what,
    void* value)
{
    return get_value(reinterpret_cast<NPP>(instance), what, value);
}
