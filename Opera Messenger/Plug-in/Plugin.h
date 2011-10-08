#ifndef __PLUGIN__
#define __PLUGIN__


// Standard library
#include <string>

// NPAPI
#include <npfunctions.h>

#include <eon/library/Object.h>


// TODO: Add documentation.
class Plugin : public eon::library::Object, public NPObject {
public:
    static NPNetscapeFuncs* host;
    
    
private:
    static NPClass _class_implementation;
    
    
public:
    static void finalize_host();
    
    
    static const char* get_plugin_description() /* = 0 */;
    
    
    static const char* get_plugin_mime_description() /* = 0 */;
    
    
    static const char* get_plugin_name() /* = 0 */;
    
    
    static NPError get_plugin_value(
        NPP instance,
        NPPVariable what,
        void* value);
    
    
    static Plugin* allocate_instance() /* = 0 */;
    
    
    static void initialize_host(NPNetscapeFuncs* new_host);
    
    
    static void initialize_plugin(NPPluginFuncs* plugin);
    
    
private:
    static NPObject* allocate(NPP instance, NPClass* class_implementation);
    
    
    static void deallocate(NPObject* plugin);
    
    
    static NPError finalize_plugin_instance(NPP instance, NPSavedData** data);
    
    
    static bool get_property_wrapper(
        NPObject* plugin,
        NPIdentifier identifier,
        NPVariant* result);
    
    
    static NPError handle_plugin_event(NPP instance, void* event);
    
    
    static bool has_method_wrapper(NPObject* plugin, NPIdentifier identifier);
    
    
    static bool has_property_wrapper(NPObject* plugin, NPIdentifier identifier);
    
    
    static NPError initialize_plugin_instance(
        NPMIMEType type,
        NPP instance,
        uint16_t mode,
        int16_t nr_arguments,
        char* argn[],
        char* argv[],
        NPSavedData* data);
    
    
    static bool invoke_wrapper(
        NPObject* plugin,
        NPIdentifier identifier,
        const NPVariant* arguments,
        uint32_t nr_arguments,
        NPVariant* result);
    
    
    static bool invoke_default_wrapper(
        NPObject* plugin,
        const NPVariant* arguments,
        uint32_t nr_arguments,
        NPVariant* result);
    
    
    static bool remove_property_wrapper(
        NPObject* plugin,
        NPIdentifier identifier);
    
    
    static bool set_property_wrapper(
        NPObject* plugin,
        NPIdentifier identifier,
        const NPVariant* value);
    
    
    static NPError set_plugin_window(NPP instance, NPWindow* window);
    
    
public:
    virtual bool get_property(NPIdentifier name, NPVariant* result);
    
    
    virtual bool has_method(NPIdentifier name);
    
    
    virtual bool has_property(std::string name);
    
    
    virtual bool invoke(
        NPIdentifier name,
        const NPVariant* arguments,
        uint32_t nr_arguments,
        NPVariant* result);
    
    
    virtual bool invoke_default(
        const NPVariant* arguments,
        uint32_t nr_arguments,
        NPVariant* result);
    
    
    virtual bool remove_property(NPIdentifier name);
    
    
    virtual bool set_property(NPIdentifier name, const NPVariant* value);
};


#endif
