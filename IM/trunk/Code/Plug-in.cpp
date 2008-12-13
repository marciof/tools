#include <fstream>
#include <npapi.h>
#include <npupp.h>
#include <npruntime.h>


static NPObject* so = NULL;
static NPNetscapeFuncs* npnfuncs = NULL;
static std::ofstream log("npIM.log");


//
// NPN (browser related)
//

static bool hasMethod(NPObject* obj, NPIdentifier methodName) {
    log << "hasMethod\n";
    return true;
}


static bool invokeDefault(NPObject* obj, const NPVariant* args, uint32_t argCount, NPVariant* result) {
    log << "invokeDefault\n";
    result->type = NPVariantType_Int32;
    result->value.intValue = 1024;
    return true;
}


static bool invoke(NPObject* obj, NPIdentifier methodName, const NPVariant* args, uint32_t argCount, NPVariant* result) {
    log << "invoke\n";
    char* name = npnfuncs->utf8fromidentifier(methodName);
    
    if(name && !strcmp((const char *)name, "foo")) {
        return invokeDefault(obj, args, argCount, result);
    }
    else {
        // aim exception handling
        npnfuncs->setexception(obj, "exception during invocation");
        return false;
    }
}


static bool hasProperty(NPObject* obj, NPIdentifier propertyName) {
    log << "hasProperty\n";
    return false;
}


static bool getProperty(NPObject* obj, NPIdentifier propertyName, NPVariant* result) {
    log << "getProperty\n";
    return false;
}


static NPClass npcRefObject = {
    NP_CLASS_STRUCT_VERSION,
    NULL,
    NULL,
    NULL,
    hasMethod,
    invoke,
    invokeDefault,
    hasProperty,
    getProperty,
    NULL,
    NULL,
};


//
// NPP (plug-in related)
//

static NPError create(NPMIMEType pluginType, NPP instance, uint16 mode, int16 argc, char* argn[], char* argv[], NPSavedData* saved) {
    log << "new\n";
    return NPERR_NO_ERROR;
}


static NPError destroy(NPP instance, NPSavedData** save) {
    if(so)
        npnfuncs->releaseobject(so);
    so = NULL;
    log << "destroy\n";
    return NPERR_NO_ERROR;
}


static NPError getValue(NPP instance, NPPVariable variable, void* value) {
    switch(variable) {
    default:
        log << "getvalue - default\n";
        return NPERR_GENERIC_ERROR;
    case NPPVpluginNameString:
        log << "getvalue - name string\n";
        *((char **)value) = "IM";
        break;
    case NPPVpluginDescriptionString:
        log << "getvalue - description string\n";
        *((char **)value) = "Instant messenger plug-in";
        break;
    case NPPVpluginScriptableNPObject:
        log << "getvalue - scriptable object\n";
        if(!so)
            so = npnfuncs->createobject(instance, &npcRefObject);
        npnfuncs->retainobject(so);
        *(NPObject **)value = so;
        break;
    case NPPVpluginNeedsXEmbed:
        log << "getvalue - xembed\n";
        *((PRBool *)value) = PR_FALSE;
        break;
    }
    return NPERR_NO_ERROR;
}


static NPError handleEvent(NPP instance, void* ev) {
    log << "handleEvent\n";
    return NPERR_NO_ERROR;
}


static NPError setWindow(NPP instance, NPWindow* pNPWindow) {
    log << "setWindow\n";
    return NPERR_NO_ERROR;
}


//
// Interface
//

extern "C"
NPError OSCALL NP_GetEntryPoints(NPPluginFuncs* nppfuncs) {
    log << "NP_GetEntryPoints\n";

    nppfuncs->version = (NP_VERSION_MAJOR << 8) | NP_VERSION_MINOR;
    nppfuncs->newp = create;
    nppfuncs->destroy = destroy;
    nppfuncs->getvalue = getValue;
    nppfuncs->event = handleEvent;
    nppfuncs->setwindow = setWindow;

    return NPERR_NO_ERROR;
}


extern "C"
NPError OSCALL NP_Initialize(NPNetscapeFuncs* npnf) {
    log << "NP_Initialize\n";

    if(npnf == NULL)
        return NPERR_INVALID_FUNCTABLE_ERROR;

    if (((npnf->version >> 8) & 0xFF) > NP_VERSION_MAJOR)
        return NPERR_INCOMPATIBLE_VERSION_ERROR;

    npnfuncs = npnf;
    return NPERR_NO_ERROR;
}


extern "C"
NPError OSCALL NP_Shutdown() {
    log << "NP_Shutdown\n";
    return NPERR_NO_ERROR;
}


extern "C"
char* NP_GetMIMEDescription() {
    log << "NP_GetMIMEDescription\n";
    return "application/x-im::";
}
