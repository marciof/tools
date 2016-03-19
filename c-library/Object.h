#ifndef __EON__LIBRARY__OBJECT__
#define __EON__LIBRARY__OBJECT__


/**
 * @file
 * @brief Root class
 */


namespace eon {
namespace library {
    /**
     * Base class of the type hierarchy.
     */
    class Object {
    public:
        virtual ~Object() {
        }
    };
}}


#endif
