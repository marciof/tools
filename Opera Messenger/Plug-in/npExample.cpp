#include <iostream>
#include <string>

#include <npapi.h>
#include <npfunctions.h>
#include <npruntime.h>
#include <nptypes.h>
#include <xpcom-config.h>

#include "npExample.h"


static NPObject* _pluginObj = NULL;
static NPNetscapeFuncs* _browser = NULL;


static bool hasMethod(NPObject* obj, NPIdentifier name) {
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
    return true;
}


static bool invokeDefault(
    NPObject* obj,
    const NPVariant* argv,
    uint32_t argc,
    NPVariant* result)
{
    std::cout << __func__ << ": argc=" << argc << std::endl;
    INT32_TO_NPVARIANT(12345, *result);
    return true;
}


static bool invoke(
    NPObject* obj,
    NPIdentifier name,
    const NPVariant* argv,
    uint32_t argc,
    NPVariant* result)
{
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << " argc=" << argc << std::endl;
    
    if (cname == "test") {
        return invokeDefault(obj, argv, argc, result);
    }
    else {
        _browser->setexception(obj, "Exception during invocation.");
        return false;
    }
}


static bool hasProperty(NPObject* obj, NPIdentifier name) {
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
    return false;
}


static bool getProperty(NPObject* obj, NPIdentifier name, NPVariant* result) {
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
    return false;
}


static bool setProperty(NPObject* obj, NPIdentifier name,
                        const NPVariant* value)
{
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
    return false;
}


static bool removeProperty(NPObject* obj, NPIdentifier name) {
    std::string cname = _browser->utf8fromidentifier(name);
    std::cout << __func__ << ": name=" << cname << std::endl;
    return false;
}


static NPClass _pluginClass = {
    NP_CLASS_STRUCT_VERSION,
    NULL,
    NULL,
    NULL,
    hasMethod,
    invoke,
    invokeDefault,
    hasProperty,
    getProperty,
    setProperty,
    removeProperty,
};


static NPError create(
    NPMIMEType type,
    NPP instance,
    uint16_t mode,
    int16_t argc,
    char* argn[],
    char* argv[],
    NPSavedData* data)
{
    std::cout << __func__ << ": mode=" << mode << " argc=" << argc << std::endl;
    return NPERR_NO_ERROR;
}


static NPError destroy(NPP instance, NPSavedData** data) {
    std::cout << __func__ << std::endl;
    
    if (_pluginObj != NULL) {
        _browser->releaseobject(_pluginObj);
        _pluginObj = NULL;
    }
    
    return NPERR_NO_ERROR;
}


static NPError getValue(NPP instance, NPPVariable what, void* value) {
    std::cout << __func__ << ": what=" << what << " value=" << value << std::endl;
    
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
        if (_pluginObj == NULL) {
            _pluginObj = _browser->createobject(instance, &_pluginClass);
        }
        _browser->retainobject(_pluginObj);
        *reinterpret_cast<NPObject**>(value) = _pluginObj;
        break;
    default:
        return NPERR_GENERIC_ERROR;
    }
    
    return NPERR_NO_ERROR;
}


static NPError handleEvent(NPP instance, void* event) {
    std::cout << __func__ << std::endl;
    return NPERR_NO_ERROR;
}


static NPError setWindow(NPP instance, NPWindow* window) {
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
    plugin->getvalue = getValue;
    plugin->event = handleEvent;
    plugin->setwindow = setWindow;
    
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
    return const_cast<char*>(PLUGIN_MIME_TYPE "::");
}


extern "C" NPError OSCALL NP_GetValue(
    void* instance,
    NPPVariable what,
    void* value)
{
    return getValue(reinterpret_cast<NPP>(instance), what, value);
}
