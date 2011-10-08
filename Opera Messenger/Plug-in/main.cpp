// Standard library.
#include <iostream>
#include <string>

// libPurple
#include <purple.h>

// NPAPI
#include <npapi.h>
#include <npfunctions.h>

#include <eon/library/features.h>
#include <eon/library/Object.h>

#include "main.h"


class Plugin : public eon::library::Object, public NPObject {
public:
    static NPNetscapeFuncs* host;
    
    
private:
    static NPClass _class_implementation;
    
    
public:
    static void finalize_host() {
        std::cout << "Finalize; host=" << host << std::endl;
        host = NULL;
    }
    
    
    static NPError get_plugin_value(
        NPP instance,
        NPPVariable what,
        void* value)
    {
        std::cout << "Get plug-in value"
            << "; instance=" << instance
            << "; what=" << what
            << "; value=" << value
            << std::endl;
        
        if (value == NULL) {
            return NPERR_INVALID_PARAM;
        }
        
        if (what == NPPVpluginNameString) {
            *static_cast<const char**>(value) = PLUGIN_NAME;
        }
        else if (what == NPPVpluginDescriptionString) {
            *static_cast<const char**>(value) = PLUGIN_DESCRIPTION;
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
    
    
    static Plugin* initialize();
    
    
    static void initialize_host(NPNetscapeFuncs* new_host) {
        std::cout << "Initialize; host=" << host << std::endl;
        host = new_host;
    }
    
    
    static void initialize_plugin(NPPluginFuncs* plugin) {
        plugin->version = (NP_VERSION_MAJOR << 8) | NP_VERSION_MINOR;
        plugin->newp = initialize_plugin_instance;
        plugin->destroy = finalize_plugin_instance;
        plugin->getvalue = get_plugin_value;
        plugin->event = handle_plugin_event;
        plugin->setwindow = set_plugin_window;
    }
    
    
private:
    static NPObject* allocate(
        UNUSED NPP instance,
        UNUSED NPClass* class_implementation)
    {
        return initialize();
    }
    
    
    static void deallocate(NPObject* plugin) {
        delete static_cast<Plugin*>(plugin);
    }
    
    
    static NPError finalize_plugin_instance(NPP instance, NPSavedData** data) {
        std::cout << "Finalize instance"
            << "; plugin=" << instance->pdata
            << "; data=" << data
            << std::endl;
        
        host->releaseobject(static_cast<NPObject*>(instance->pdata));
        return NPERR_NO_ERROR;
    }
    
    
    static bool get_property_wrapper(
        NPObject* plugin,
        NPIdentifier identifier,
        NPVariant* result)
    {
        return static_cast<Plugin*>(plugin)->get_property(
            identifier, result);
    }
    
    
    static NPError handle_plugin_event(UNUSED NPP instance, UNUSED void* event) {
        return NPERR_NO_ERROR;
    }
    
    
    static bool has_method_wrapper(NPObject* plugin, NPIdentifier identifier) {
        return static_cast<Plugin*>(plugin)->has_method(identifier);
    }
    
    
    static bool has_property_wrapper(
        NPObject* plugin,
        NPIdentifier identifier)
    {
        char* name = host->utf8fromidentifier(identifier);
        bool result = static_cast<Plugin*>(plugin)->has_property(name);
        
        host->memfree(name);
        return result;
    }
    
    
    static NPError initialize_plugin_instance(
        NPMIMEType type,
        NPP instance,
        UNUSED uint16_t mode,
        UNUSED int16_t nr_arguments,
        UNUSED char* argn[],
        UNUSED char* argv[],
        UNUSED NPSavedData* data)
    {
        instance->pdata = NULL;
        
        std::cout << "Initialize instance"
            << "; plugin=" << instance->pdata
            << "; type=" << type
            << std::endl;
        
        return NPERR_NO_ERROR;
    }
    
    
    static bool invoke_wrapper(
        NPObject* plugin,
        NPIdentifier identifier,
        const NPVariant* arguments,
        uint32_t nr_arguments,
        NPVariant* result)
    {
        return static_cast<Plugin*>(plugin)->invoke(
            identifier, arguments, nr_arguments, result);
    }
    
    
    static bool invoke_default_wrapper(
        NPObject* plugin,
        const NPVariant* arguments,
        uint32_t nr_arguments,
        NPVariant* result)
    {
        return static_cast<Plugin*>(plugin)->invoke_default(
            arguments, nr_arguments, result);
    }
    
    
    static bool remove_property_wrapper(
        NPObject* plugin,
        NPIdentifier identifier)
    {
        return static_cast<Plugin*>(plugin)->remove_property(identifier);
    }
    
    
    static bool set_property_wrapper(
        NPObject* plugin,
        NPIdentifier identifier,
        const NPVariant* value)
    {
        return static_cast<Plugin*>(plugin)->set_property(
            identifier, value);
    }
    
    
    static NPError set_plugin_window(UNUSED NPP instance, UNUSED NPWindow* window) {
        return NPERR_NO_ERROR;
    }
    
    
public:
    virtual bool get_property(NPIdentifier name, NPVariant* result) = 0;
    virtual bool has_method(NPIdentifier name) = 0;
    
    
    virtual bool has_property(UNUSED std::string name) {
        return false;
    }
    
    
    virtual bool invoke(NPIdentifier name, const NPVariant* arguments, uint32_t nr_arguments, NPVariant* result) = 0;
    virtual bool invoke_default(const NPVariant* arguments, uint32_t nr_arguments, NPVariant* result) = 0;
    virtual bool remove_property(NPIdentifier name) = 0;
    virtual bool set_property(NPIdentifier name, const NPVariant* value) = 0;
};


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


class Purple : public Plugin {
public:
    bool get_property(NPIdentifier name, UNUSED NPVariant* result) {
        std::string cname = host->utf8fromidentifier(name);
        std::cout << FUNCTION_NAME << "; name=" << cname << std::endl;
        return false;
    }
    
    
    bool has_method(NPIdentifier name) {
        std::string cname = host->utf8fromidentifier(name);
        std::cout << FUNCTION_NAME << "; name=" << cname << std::endl;
        return false;
    }
    
    
    bool has_property(std::string name) {
        std::cout << FUNCTION_NAME << "; name=" << name << std::endl;
        return false;
    }
    
    
    bool invoke(
        NPIdentifier name,
        UNUSED const NPVariant* arguments,
        uint32_t nr_arguments,
        UNUSED NPVariant* result)
    {
        std::string cname = host->utf8fromidentifier(name);
        
        std::cout << FUNCTION_NAME
            << "; name=" << cname
            << "; #args=" << nr_arguments
            << std::endl;
        
        host->setexception(this, "Exception during invocation.");
        return false;
    }
    
    
    bool invoke_default(
        UNUSED const NPVariant* arguments,
        uint32_t nr_arguments,
        UNUSED NPVariant* result)
    {
        std::cout << FUNCTION_NAME << "; #args=" << nr_arguments << std::endl;
        return false;
    }
    
    
    bool remove_property(NPIdentifier name) {
        std::string cname = host->utf8fromidentifier(name);
        std::cout << FUNCTION_NAME << "; name=" << cname << std::endl;
        return false;
    }
    
    
    bool set_property(NPIdentifier name, UNUSED const NPVariant* value) {
        std::string cname = host->utf8fromidentifier(name);
        std::cout << FUNCTION_NAME << "; name=" << cname << std::endl;
        return false;
    }
};


Plugin* Plugin::initialize() {
    return new Purple();
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


PUBLIC char* NP_GetMIMEDescription() {
    // <MIME Type>:<extension>:<description>
    return const_cast<char*>(PLUGIN_MIME_TYPE ": : ");
}


PUBLIC NPError OSCALL NP_GetValue(
    void* instance,
    NPPVariable what,
    void* value)
{
    return Purple::get_plugin_value(
        static_cast<NPP>(instance), what, value);
}
