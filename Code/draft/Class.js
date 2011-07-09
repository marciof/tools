function extend(subClass, baseClass) {
    function InheritanceLink() {
    }
 
    InheritanceLink.prototype = baseClass.prototype;
    subClass.prototype = new InheritanceLink();
    subClass.prototype.constructor = subClass;
}


/**
 * Extends a class.
 *
 * @param {Function} BaseClass class to extend
 */
Function.prototype.extend = function(BaseClass) {
    // Unless an intermediate class is used, the prototype of the sub class
    // would also be the same of the base class. If so, any changes in the
    // prototype of the sub class would also be reflected in the base class.
    function InheritanceLink() {
    }
    
    InheritanceLink.prototype = BaseClass.prototype;
    this.prototype = new InheritanceLink();
    this.prototype.constructor = this;
};


this.isImplemented = function(Interface, object) {
    if (object instanceof Interface) {
        return false;
    }
    
    for (var prop in Interface.prototype) {
        var method = Interface.prototype[prop];
        
        if (typeof method != 'function') {
            continue;
        }
        if (!(prop in object) || (typeof object[prop] != 'function')) {
            return false;
        }
        if (method.length != object[prop].length) {
            return false;
        }
    }
    
    return true;
};


/**
 * Implements an abstract class.
 *
 * @param {Function} AbstractClass class whose methods are to be copied
 * @param {Function} Class class to be implemented
 */
this.implement = function(AbstractClass, Class) {
    var methods = Interface.prototype;
    
    for (var method in methods) {
        if (typeof methods[method] == 'function') {
            Class.prototype[method] = methods[method];
        }
    }
};


////////////////////////////////////////////////////////////////////////////////


var beats = new GenericFunction();

beats.overload([Thing, Thing], function(a, b) {
    return false;
});
beats.overload([Paper, Rock], function(a, b) {
    return true;
});
beats.overload([Rock, Scissor], function(a, b) {
    return true;
});
beats.overload([Scissor, Paper], function(a, b) {
    return true;
});


var greet = new GenericFunction();

greet.overload([], function() {
    alert('Hey!');
});
greet.overload([String], function(name) {
    alert('Hi ' + name + '!');
});
