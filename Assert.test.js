/**
 * @fileoverview Tests assertions.
 * @author Márcio Faustino
 */


test({
    testAssert: function() {
        assert(true);
        assert(1);
        assert('...');
        assert({});
        assert([]);
    },
    
    testAssertEquals: function() {
        assert.equals('', '');
        assert.equals(-0, +0);
        assert.equals(1, 1.0);
    },
    
    testAssertException: function() {
        assert.exception(Error, function() {
            throw Error();
        });
    },
    
    testAssertFalse: function() {
        assert.False(false);
    },
    
    testAssertNull: function() {
        assert.Null(null);
    },
    
    testAssertTrue: function() {
        assert.True(true);
    },
    
    testAssertUndefined: function() {
        assert.Undefined(undefined);
    },
    
    testCorrectNumberOfArguments: function() {
        assert.exception(SyntaxError, function() {assert()});
        assert.exception(SyntaxError, function() {assert(1, 2)});
        assert.exception(SyntaxError, function() {assert.equals(1)});
        assert.exception(SyntaxError, function() {assert.equals(1, 2, 3)});
        assert.exception(SyntaxError, function() {assert.exception(Error)});
        assert.exception(SyntaxError, function() {assert.exception(Error, 2, 3)});
        assert.exception(SyntaxError, function() {assert.False()});
        assert.exception(SyntaxError, function() {assert.False(1, 2)});
        assert.exception(SyntaxError, function() {assert.Null()});
        assert.exception(SyntaxError, function() {assert.Null(1, 2)});
        assert.exception(SyntaxError, function() {assert.True()});
        assert.exception(SyntaxError, function() {assert.True(1, 2)});
        assert.exception(SyntaxError, function() {assert.Undefined()});
        assert.exception(SyntaxError, function() {assert.Undefined(1, 2)});
    },
    
    testAssertionFailures: function() {
        assert.exception(Error, function() {assert('')});
        assert.exception(Error, function() {assert.equals(true, false)});
        assert.exception(Error, function() {assert.equals(null, undefined)});
        assert.exception(Error, function() {assert.False(0)});
        assert.exception(Error, function() {assert.Null(undefined)});
        assert.exception(Error, function() {assert.True(1)});
        assert.exception(Error, function() {assert.Undefined(null)});
        
        assert.exception(Error, function() {
            assert.exception(SyntaxError, function() {throw RangeError()});
        });
        
        assert.exception(Error, function() {
            assert.exception(Error, function() {});
        });
    }
});
