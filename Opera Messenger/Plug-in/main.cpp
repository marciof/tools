// Standard library
#include <iostream>

// libPurple
#include <purple.h>

#include <eon/library/features.h>

#include "main.h"
#include "Plugin.h"


// TODO: Improve logging.
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


Plugin* Plugin::allocate_instance() {
    return new Purple();
}
