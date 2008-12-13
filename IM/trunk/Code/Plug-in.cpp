#include <fstream>
#include <npapi.h>
#include <npupp.h>
#include <npruntime.h>
#include <string>


static NPObject* _pluginObj = NULL;
static NPNetscapeFuncs* _browser = NULL;
static std::ofstream _log("npIM.log");


static bool hasMethod(NPObject* obj, NPIdentifier name) {
    _log << "hasMethod\n";
    return true;
}


static bool invokeDefault(NPObject* obj, const NPVariant* argv, uint32_t argc, NPVariant* result) {
    _log << "invokeDefault\n";

    result->type = NPVariantType_Int32;
    result->value.intValue = 1024;
    return true;
}


static bool invoke(NPObject* obj, NPIdentifier name, const NPVariant* argv, uint32_t argc, NPVariant* result) {
    _log << "invoke\n";
    std::string cname = _browser->utf8fromidentifier(name);
    
    if (cname == "foo") {
        return invokeDefault(obj, argv, argc, result);
    }
    else {
        _browser->setexception(obj, "exception during invocation");
        return false;
    }
}


static bool hasProperty(NPObject* obj, NPIdentifier name) {
    _log << "hasProperty\n";
    return false;
}


static bool getProperty(NPObject* obj, NPIdentifier name, NPVariant* result) {
    _log << "getProperty\n";
    return false;
}


static bool setProperty(NPObject* obj, NPIdentifier name, const NPVariant* value) {
    _log << "setProperty\n";
    return false;
}


static bool removeProperty(NPObject* obj, NPIdentifier name) {
    _log << "removeProperty\n";
    return false;
}


static NPClass _pluginClass = {
    NP_CLASS_STRUCT_VERSION,
    NULL, // Allocate.
    NULL, // Deallocate.
    NULL, // Invalidate.
    hasMethod,
    invoke,
    invokeDefault,
    hasProperty,
    getProperty,
    setProperty,
    removeProperty,
};


static NPError create(NPMIMEType type, NPP instance, uint16 mode, int16 argc, char* argn[], char* argv[], NPSavedData* data) {
    _log << "create\n";
    return NPERR_NO_ERROR;
}


static NPError destroy(NPP instance, NPSavedData** data) {
    _log << "destroy\n";
    
    if (_pluginObj != NULL) {
        _browser->releaseobject(_pluginObj);
        _pluginObj = NULL;
    }
    
    return NPERR_NO_ERROR;
}


static NPError getValue(NPP instance, NPPVariable what, void* value) {
    _log << "getValue\n";
    
    switch (what) {
    case NPPVpluginNameString:
        *(char**) value = "IM";
        break;
    case NPPVpluginDescriptionString:
        *(char**) value = "Instant messenger plug-in";
        break;
    case NPPVpluginScriptableNPObject:
        if (_pluginObj == NULL) {
            _pluginObj = _browser->createobject(instance, &_pluginClass);
        }
        _browser->retainobject(_pluginObj);
        *(NPObject**) value = _pluginObj;
        break;
    case NPPVpluginNeedsXEmbed:
        *(PRBool*) value = PR_FALSE;
        break;
    default:
        return NPERR_GENERIC_ERROR;
    }
    
    return NPERR_NO_ERROR;
}


static NPError handleEvent(NPP instance, void* event) {
    _log << "handleEvent\n";
    return NPERR_NO_ERROR;
}


static NPError setWindow(NPP instance, NPWindow* window) {
    _log << "setWindow\n";
    return NPERR_NO_ERROR;
}


extern "C"
NPError OSCALL NP_GetEntryPoints(NPPluginFuncs* plugin) {
    _log << "NP_GetEntryPoints\n";
    
    plugin->version = (NP_VERSION_MAJOR << 8) | NP_VERSION_MINOR;
    plugin->newp = create;
    plugin->destroy = destroy;
    plugin->getvalue = getValue;
    plugin->event = handleEvent;
    plugin->setwindow = setWindow;
    
    return NPERR_NO_ERROR;
}


extern "C"
NPError OSCALL NP_Initialize(NPNetscapeFuncs* browser) {
    _log << "NP_Initialize\n";

    if (browser == NULL) {
        return NPERR_INVALID_FUNCTABLE_ERROR;
    }
    if (((browser->version >> 8) & 0xFF) > NP_VERSION_MAJOR) {
        return NPERR_INCOMPATIBLE_VERSION_ERROR;
    }
    
    _browser = browser;
    return NPERR_NO_ERROR;
}


extern "C"
NPError OSCALL NP_Shutdown() {
    _log << "NP_Shutdown\n";
    _browser = NULL;
    return NPERR_NO_ERROR;
}


extern "C"
char* NP_GetMIMEDescription() {
    _log << "NP_GetMIMEDescription\n";
    return "application/x-im::";
}
