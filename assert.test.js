/**
 * @fileoverview Tests assertions.
 * @author Márcio Faustino
 */


test({
    assert: function() {
        assert(true);
        assert(1);
        assert('...');
        assert({});
        assert([]);
    },
    
    assertEquals: function() {
        assert.equals('', '');
        assert.equals(-0, +0);
        assert.equals(1, 1.0);
    },
    
    assertException: function() {
        assert.exception(Error, function() {
            throw Error();
        });
    },
    
    assertFalse: function() {
        assert.False(false);
    },
    
    assertNull: function() {
        assert.Null(null);
    },
    
    assertTrue: function() {
        assert.True(true);
    },
    
    assertUndefined: function() {
        assert.Undefined(undefined);
    },
    
    correctNumberOfArguments: function() {
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
    
    assertionFailures: function() {
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
