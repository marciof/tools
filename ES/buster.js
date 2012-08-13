'use strict';


var config = module.exports,
    assertions = require('buster').assertions;

config['Node based tests'] = {
    environment: 'node',
    sources: ['*.js'],
    tests: ['*.test.js']
};


assertions.add('isUndefined', {
    assertMessage: 'Expected ${0} to be undefined',
    refuteMessage: 'Expected ${0} to not be undefined',
    
    assert: function (value) {
        // Don't use `undefined` in case it has been redefined.
        return value === void(0);
    }
});


assertions.add('throws', {
    assertMessage: 'Expected ${name} to be thrown (got ${actualName})',
    refuteMessage: 'Expected ${name} to not be thrown',
    
    assert: function (fn, Exception) {
        this.name = '`' + Exception.prototype.name + '`';
        
        try {
            fn();
            this.actualName = 'nothing';
            return false;
        }
        catch (exception) {
            this.actualName = '`' + exception.name + '`';
            return exception instanceof Exception;
        }
    }
});
