// TODO: Improve logging.


// Standard library
#include <iostream>

#include <eon/library/features.h>
#include <eon/library/types.h>

#include "Plugin.h"


NPNetscapeFuncs* Plugin::host = NULL;

NPClass Plugin::_class_implementation = {
    NP_CLASS_STRUCT_VERSION,
    Plugin::allocate,
    Plugin::deallocate,
    NULL,
    Plugin::has_method_wrapper,
    Plugin::invoke_wrapper,
    Plugin::invoke_default_wrapper,
    Plugin::has_property_wrapper,
    Plugin::get_property_wrapper,
    Plugin::set_property_wrapper,
    Plugin::remove_property_wrapper,
    NULL,
    NULL,
};


void Plugin::finalize_host() {
    std::cout << "Finalize host; host=" << host << std::endl;
    host = NULL;
}


NPError Plugin::get_plugin_value(NPP instance, NPPVariable what, void* value) {
    std::cout << "Get plug-in value"
        << "; instance=" << instance
        << "; what=" << what
        << "; value=" << value
        << std::endl;
    
    if (value == NULL) {
        return NPERR_INVALID_PARAM;
    }
    
    if (what == NPPVpluginNameString) {
        *static_cast<const char**>(value) = get_plugin_name();
    }
    else if (what == NPPVpluginDescriptionString) {
        *static_cast<const char**>(value) = get_plugin_description();
    }
    else if (what == NPPVpluginScriptableNPObject) {
        if (instance->pdata == NULL) {
            instance->pdata = host->createobject(
                instance, &Plugin::_class_implementation);
        }
        
        host->retainobject(static_cast<NPObject*>(instance->pdata));
        *static_cast<void**>(value) = instance->pdata;
    }
    else {
        return NPERR_GENERIC_ERROR;
    }
    
    return NPERR_NO_ERROR;
}


void Plugin::initialize_host(NPNetscapeFuncs* new_host) {
    std::cout << "Initialize host; host=" << host << std::endl;
    host = new_host;
}


void Plugin::initialize_plugin(NPPluginFuncs* plugin) {
    std::cout << "Initialize plug-in; plugin=" << plugin << std::endl;
    
    plugin->version = (NP_VERSION_MAJOR << 8) | NP_VERSION_MINOR;
    plugin->newp = initialize_plugin_instance;
    plugin->destroy = finalize_plugin_instance;
    plugin->getvalue = get_plugin_value;
    plugin->event = handle_plugin_event;
    plugin->setwindow = set_plugin_window;
}


NPObject* Plugin::allocate(
    UNUSED NPP instance,
    UNUSED NPClass* class_implementation)
{
    return allocate_instance();
}


void Plugin::deallocate(NPObject* plugin) {
    delete static_cast<Plugin*>(plugin);
}


NPError Plugin::finalize_plugin_instance(NPP instance, NPSavedData** data) {
    std::cout << "Finalize plug-in instance"
        << "; plugin=" << instance->pdata
        << "; data=" << data
        << std::endl;
    
    host->releaseobject(static_cast<NPObject*>(instance->pdata));
    return NPERR_NO_ERROR;
}


bool Plugin::get_property_wrapper(
    NPObject* plugin,
    NPIdentifier identifier,
    NPVariant* result)
{
    return static_cast<Plugin*>(plugin)->get_property(
        identifier, result);
}


NPError Plugin::handle_plugin_event(UNUSED NPP instance, UNUSED void* event) {
    return NPERR_NO_ERROR;
}


bool Plugin::has_method_wrapper(NPObject* plugin, NPIdentifier identifier) {
    return static_cast<Plugin*>(plugin)->has_method(identifier);
}


bool Plugin::has_property_wrapper(NPObject* plugin, NPIdentifier identifier) {
    char* name = host->utf8fromidentifier(identifier);
    bool result = static_cast<Plugin*>(plugin)->has_property(name);
    
    host->memfree(name);
    return result;
}


NPError Plugin::initialize_plugin_instance(
    UNUSED NPMIMEType type,
    NPP instance,
    UNUSED uint16_t mode,
    UNUSED int16_t nr_arguments,
    UNUSED char* argn[],
    UNUSED char* argv[],
    NPSavedData* data)
{
    instance->pdata = NULL;
    
    std::cout << "Initialize plug-in instance"
        << "; plugin=" << instance->pdata
        << "; data=" << data
        << std::endl;
    
    return NPERR_NO_ERROR;
}


bool Plugin::invoke_wrapper(
    NPObject* plugin,
    NPIdentifier identifier,
    const NPVariant* arguments,
    uint32_t nr_arguments,
    NPVariant* result)
{
    return static_cast<Plugin*>(plugin)->invoke(
        identifier, arguments, nr_arguments, result);
}


bool Plugin::invoke_default_wrapper(
    NPObject* plugin,
    const NPVariant* arguments,
    uint32_t nr_arguments,
    NPVariant* result)
{
    return static_cast<Plugin*>(plugin)->invoke_default(
        arguments, nr_arguments, result);
}


bool Plugin::remove_property_wrapper(
    NPObject* plugin,
    NPIdentifier identifier)
{
    return static_cast<Plugin*>(plugin)->remove_property(identifier);
}


bool Plugin::set_property_wrapper(
    NPObject* plugin,
    NPIdentifier identifier,
    const NPVariant* value)
{
    return static_cast<Plugin*>(plugin)->set_property(
        identifier, value);
}


NPError Plugin::set_plugin_window(
    UNUSED NPP instance,
    UNUSED NPWindow* window)
{
    return NPERR_NO_ERROR;
}


bool Plugin::get_property(UNUSED NPIdentifier name, UNUSED NPVariant* result) {
    return false;
}


bool Plugin::has_method(UNUSED NPIdentifier name) {
    return false;
}


bool Plugin::has_property(UNUSED std::string name) {
    return false;
}


bool Plugin::invoke(
    UNUSED NPIdentifier name,
    UNUSED const NPVariant* arguments,
    UNUSED uint32_t nr_arguments,
    UNUSED NPVariant* result)
{
    return false;
}


bool Plugin::invoke_default(
    UNUSED const NPVariant* arguments,
    UNUSED uint32_t nr_arguments,
    UNUSED NPVariant* result)
{
    return false;
}


bool Plugin::remove_property(UNUSED NPIdentifier name) {
    return false;
}


bool Plugin::set_property(
    UNUSED NPIdentifier name,
    UNUSED const NPVariant* value)
{
    return false;
}


PUBLIC NPError OSCALL NP_GetEntryPoints(NPPluginFuncs* plugin) {
    if (plugin == NULL) {
        return NPERR_INVALID_FUNCTABLE_ERROR;
    }
    
    Plugin::initialize_plugin(plugin);
    return NPERR_NO_ERROR;
}


PUBLIC NPError OSCALL NP_Initialize(
    NPNetscapeFuncs* host
#ifndef _WINDOWS
    , NPPluginFuncs* plugin
#endif
) {
    if (host == NULL) {
        return NPERR_INVALID_FUNCTABLE_ERROR;
    }
    if ((host->version >> 8) > NP_VERSION_MAJOR) {
        return NPERR_INCOMPATIBLE_VERSION_ERROR;
    }
    
    Plugin::initialize_host(host);
    
#ifndef _WINDOWS
    return NP_GetEntryPoints(plugin);
#else
    return NPERR_NO_ERROR;
#endif
}


PUBLIC NPError OSCALL NP_Shutdown() {
    Plugin::finalize_host();
    return NPERR_NO_ERROR;
}


// <MIME Type>:<extension>:<description>;...
PUBLIC const char* NP_GetMIMEDescription() {
    return Plugin::get_plugin_mime_description();
}


PUBLIC NPError OSCALL NP_GetValue(
    void* instance,
    NPPVariable what,
    void* value)
{
    return Plugin::get_plugin_value(static_cast<NPP>(instance), what, value);
}
