var config = module.exports;

config['Node based tests'] = {
    environment: 'node',
    sources: ['*.js'],
    tests: ['*.test.js']
};


require('buster').assertions.add('isUndefined', {
    assertMessage: 'Expected ${0} to be undefined',
    refuteMessage: 'Expected ${0} to not be undefined',
    
    assert: function (value) {
        // Don't use `undefined` in case it has been redefined.
        return value === void(0);
    }
});
