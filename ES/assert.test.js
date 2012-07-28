/**
 * @fileOverview Tests assertions.
 * @author Márcio Faustino
 */


test({
    assert: function () {
        assert(true);
        assert(1);
        assert('...');
        assert({});
        assert([]);
    },
    
    assertEquals: function () {
        assert.identical('', '');
        assert.identical(-0, +0);
        assert.identical(1, 1.0);
    },
    
    assertException: function () {
        assert.exception(Error, function () {
            throw Error();
        });
    },
    
    assertFalse: function () {
        assert.False(false);
    },
    
    assertNaN: function () {
        assert.NaN(NaN);
    },
    
    assertNotEquals: function () {
        assert.notEquals(true, false);
        assert.notEquals(null, undefined);
        assert.notEquals(0, 0.1);
    },
    
    assertNull: function () {
        assert.Null(null);
    },
    
    assertTrue: function () {
        assert.True(true);
    },
    
    assertUndefined: function () {
        assert.Undefined(undefined);
    },
    
    correctNumberOfArguments: function () {
        assert.exception(SyntaxError, function () {assert();});
        assert.exception(SyntaxError, function () {assert(1, 2);});
        
        assert.exception(SyntaxError, function () {assert.identical(1);});
        assert.exception(SyntaxError, function () {assert.identical(1, 2, 3);});
        
        assert.exception(SyntaxError, function () {assert.exception(Error);});
        assert.exception(SyntaxError, function () {assert.exception(Error, 2, 3);});
        
        assert.exception(SyntaxError, function () {assert.False();});
        assert.exception(SyntaxError, function () {assert.False(1, 2);});
        
        assert.exception(SyntaxError, function () {assert.NaN();});
        assert.exception(SyntaxError, function () {assert.NaN(1, 2);});
        
        assert.exception(SyntaxError, function () {assert.notEquals(1);});
        assert.exception(SyntaxError, function () {assert.notEquals(1, 2, 3);});
        
        assert.exception(SyntaxError, function () {assert.Null();});
        assert.exception(SyntaxError, function () {assert.Null(1, 2);});
        
        assert.exception(SyntaxError, function () {assert.True();});
        assert.exception(SyntaxError, function () {assert.True(1, 2);});
        
        assert.exception(SyntaxError, function () {assert.Undefined();});
        assert.exception(SyntaxError, function () {assert.Undefined(1, 2);});
    },
    
    assertionFailures: function () {
        assert.exception(Error, function () {assert('');});
        assert.exception(Error, function () {assert.identical(true, false);});
        assert.exception(Error, function () {assert.identical(null, undefined);});
        assert.exception(Error, function () {assert.False(0);});
        assert.exception(Error, function () {assert.NaN(0);});
        assert.exception(Error, function () {assert.notEquals(0, 0);});
        assert.exception(Error, function () {assert.Null(undefined);});
        assert.exception(Error, function () {assert.True(1);});
        assert.exception(Error, function () {assert.Undefined(null);});
        
        assert.exception(Error, function () {
            assert.exception(SyntaxError, function () {throw RangeError();});
        });
        
        assert.exception(Error, function () {
            assert.exception(Error, function () {});
        });
    }
});
