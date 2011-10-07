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


class Plugin : public eon::library::Object {
public:
    virtual bool get_property(NPIdentifier name, NPVariant* result) = 0;
    virtual bool has_method(NPIdentifier name) = 0;
    virtual bool has_property(NPIdentifier name) = 0;
    virtual bool invoke(NPIdentifier name, const NPVariant* arguments, uint32_t nr_arguments, NPVariant* result) = 0;
    virtual bool invoke_default(const NPVariant* arguments, uint32_t nr_arguments, NPVariant* result) = 0;
    virtual bool remove_property(NPIdentifier name) = 0;
    virtual bool set_property(NPIdentifier name, const NPVariant* value) = 0;
};


struct PluginObject : public NPObject {
    static void finalize(NPObject* plugin_object) {
        delete reinterpret_cast<PluginObject*>(plugin_object);
    }
    
    
    static bool get_property(
        NPObject* plugin_object,
        NPIdentifier name,
        NPVariant* result)
    {
        return reinterpret_cast<PluginObject*>(plugin_object)
            ->_plugin->get_property(name, result);
    }
    
    
    static bool has_method(NPObject* plugin_object, NPIdentifier name) {
        return reinterpret_cast<PluginObject*>(plugin_object)
            ->_plugin->has_method(name);
    }
    
    
    static bool has_property(NPObject* plugin_object, NPIdentifier name) {
        return reinterpret_cast<PluginObject*>(plugin_object)
            ->_plugin->has_property(name);
    }
    
    
    static NPObject* initialize(NPP instance, UNUSED NPClass* class_impl) {
        return new PluginObject(reinterpret_cast<Plugin*>(instance->pdata));
    }
    
    
    static bool invoke(
        NPObject* plugin_object,
        NPIdentifier name,
        const NPVariant* arguments,
        uint32_t nr_arguments,
        NPVariant* result)
    {
        return reinterpret_cast<PluginObject*>(plugin_object)
            ->_plugin->invoke(name, arguments, nr_arguments, result);
    }
    
    
    static bool invoke_default(
        NPObject* plugin_object,
        const NPVariant* arguments,
        uint32_t nr_arguments,
        NPVariant* result)
    {
        return reinterpret_cast<PluginObject*>(plugin_object)
            ->_plugin->invoke_default(arguments, nr_arguments, result);
    }
    
    
    static bool remove_property(NPObject* plugin_object, NPIdentifier name) {
        return reinterpret_cast<PluginObject*>(plugin_object)
            ->_plugin->remove_property(name);
    }
    
    
    static bool set_property(
        NPObject* plugin_object,
        NPIdentifier name,
        const NPVariant* value)
    {
        return reinterpret_cast<PluginObject*>(plugin_object)
            ->_plugin->set_property(name, value);
    }
    
    
    static NPClass class_implementation;
    Plugin* _plugin;
    
    
    PluginObject(Plugin* plugin) : _plugin(plugin) {
    }
};


NPClass PluginObject::class_implementation = {
    NP_CLASS_STRUCT_VERSION,
    initialize,
    finalize,
    NULL,
    has_method,
    invoke,
    invoke_default,
    has_property,
    get_property,
    set_property,
    remove_property,
    NULL,
    NULL,
};


class Purple : public Plugin {
private:
    static NPNetscapeFuncs* _browser;
    
    
public:
    static void finalize() {
        std::cout << "Finalize; browser=" << _browser << std::endl;
        _browser = NULL;
    }
    
    
    static NPError finalize_instance(NPP instance, NPSavedData** data) {
        Purple* purple = reinterpret_cast<Purple*>(instance->pdata);
        
        std::cout << "Finalize instance"
            << "; instance=" << purple
            << "; data=" << data
            << std::endl;
        
        _browser->releaseobject(purple->_plugin);
        instance->pdata = NULL;
        delete purple;
        
        return NPERR_NO_ERROR;
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
            *reinterpret_cast<const char**>(value) = PLUGIN_NAME;
        }
        else if (what == NPPVpluginDescriptionString) {
            *reinterpret_cast<const char**>(value) = PLUGIN_DESCRIPTION;
        }
        else if (what == NPPVpluginScriptableNPObject) {
            Purple* purple = reinterpret_cast<Purple*>(instance->pdata);
            
            if (purple->_plugin == NULL) {
                purple->_plugin = _browser->createobject(
                    instance, &PluginObject::class_implementation);
            }
            
            _browser->retainobject(purple->_plugin);
            *reinterpret_cast<NPObject**>(value) = purple->_plugin;
        }
        else {
            return NPERR_GENERIC_ERROR;
        }
        
        return NPERR_NO_ERROR;
    }
    
    
    static void initialize(NPNetscapeFuncs* browser) {
        std::cout << "Initialize; browser=" << browser << std::endl;
        _browser = browser;
    }
    
    
    static NPError initialize_instance(
        NPMIMEType type,
        NPP instance,
        UNUSED uint16_t mode,
        UNUSED int16_t nr_arguments,
        UNUSED char* argn[],
        UNUSED char* argv[],
        UNUSED NPSavedData* data)
    {
        instance->pdata = new Purple();
        
        std::cout << "Initialize instance"
            << "; instance=" << instance->pdata
            << "; type=" << type
            << std::endl;
        
        return NPERR_NO_ERROR;
    }
    
    
private:
    NPObject* _plugin;
    
    
public:
    Purple() : _plugin(NULL) {
    }
    
    
    bool get_property(NPIdentifier name, UNUSED NPVariant* result) {
        std::string cname = _browser->utf8fromidentifier(name);
        std::cout << FUNCTION_NAME << "; name=" << cname << std::endl;
        return false;
    }
    
    
    bool has_method(NPIdentifier name) {
        std::string cname = _browser->utf8fromidentifier(name);
        std::cout << FUNCTION_NAME << "; name=" << cname << std::endl;
        return false;
    }
    
    
    bool has_property(NPIdentifier name) {
        std::string cname = _browser->utf8fromidentifier(name);
        std::cout << FUNCTION_NAME << "; name=" << cname << std::endl;
        return false;
    }
    
    
    bool invoke(
        NPIdentifier name,
        UNUSED const NPVariant* arguments,
        uint32_t nr_arguments,
        UNUSED NPVariant* result)
    {
        std::string cname = _browser->utf8fromidentifier(name);
        
        std::cout << FUNCTION_NAME
            << "; name=" << cname
            << "; #args=" << nr_arguments
            << std::endl;
        
        _browser->setexception(_plugin, "Exception during invocation.");
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
        std::string cname = _browser->utf8fromidentifier(name);
        std::cout << FUNCTION_NAME << "; name=" << cname << std::endl;
        return false;
    }
    
    
    bool set_property(NPIdentifier name, UNUSED const NPVariant* value) {
        std::string cname = _browser->utf8fromidentifier(name);
        std::cout << FUNCTION_NAME << "; name=" << cname << std::endl;
        return false;
    }
    
    
private:
    Purple(const Purple&);
    void operator=(const Purple&);
};


NPNetscapeFuncs* Purple::_browser;


static NPError handle_event(UNUSED NPP instance, UNUSED void* event) {
    return NPERR_NO_ERROR;
}


static NPError set_window(UNUSED NPP instance, UNUSED NPWindow* window) {
    return NPERR_NO_ERROR;
}


PUBLIC NPError OSCALL NP_GetEntryPoints(NPPluginFuncs* plugin_functions) {
    if (plugin_functions == NULL) {
        return NPERR_INVALID_FUNCTABLE_ERROR;
    }
    
    plugin_functions->version = (NP_VERSION_MAJOR << 8) | NP_VERSION_MINOR;
    plugin_functions->newp = Purple::initialize_instance;
    plugin_functions->destroy = Purple::finalize_instance;
    plugin_functions->getvalue = Purple::get_plugin_value;
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
    if (browser_instance == NULL) {
        return NPERR_INVALID_FUNCTABLE_ERROR;
    }
    if ((browser_instance->version >> 8) > NP_VERSION_MAJOR) {
        return NPERR_INCOMPATIBLE_VERSION_ERROR;
    }
    
    Purple::initialize(browser_instance);
    
#ifndef _WINDOWS
    NP_GetEntryPoints(plugin_functions);
#endif
    
    return NPERR_NO_ERROR;
}


PUBLIC NPError OSCALL NP_Shutdown() {
    Purple::finalize();
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
        reinterpret_cast<NPP>(instance), what, value);
}
