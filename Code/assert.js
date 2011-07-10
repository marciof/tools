/**
 * @fileOverview Implements assertions.
 * @author Márcio Faustino
 * @version 2011-07-10
 */


/**
 * Asserts a condition.
 *
 * @namespace Assertion functions.
 * @param value condition value to assert
 * @throws {Error} Assertion failed.
 */
function assert(value) {
    if (arguments.length != 1) {
        throw new SyntaxError('Wrong number of arguments');
    }
    if (!value) {
        throw new Error('Assertion failed');
    }
}


/**
 * Asserts that two values are identical.
 *
 * @param x first value to compare with
 * @param y second value to compare with
 * @throws {Error} Assertion failed.
 * @throws {SyntaxError} Wrong number of arguments.
 */
assert.equals = function(x, y) {
    if (arguments.length != 2) {
        throw new SyntaxError('Wrong number of arguments');
    }
    if (x !== y) {
        throw new Error('Assertion failed: Not identical: ' + x + ' !== ' + y);
    }
};


/**
 * Asserts that an exception is thrown.
 *
 * @param {Function} type expected exception type
 * @param {Function} code function that should throw an exception
 * @throws {Error} Assertion failed.
 * @throws {SyntaxError} Wrong number of arguments.
 */
assert.exception = function(type, code) {
    if (arguments.length != 2) {
        throw new SyntaxError('Wrong number of arguments');
    }
    
    try {
        code();
    }
    catch (exception) {
        if (exception instanceof type) {
            return;
        }
        else {
            throw new Error('Assertion failed: Unexpected exception thrown: '
                + exception);
        }
    }
    
    throw new Error('Assertion failed: Expected exception not thrown: '
        + type);
};


/**
 * Asserts that a value is false.
 *
 * @param value value to assert it's false
 * @throws {Error} Assertion failed.
 * @throws {SyntaxError} Wrong number of arguments.
 */
assert.False = function(value) {
    if (arguments.length != 1) {
        throw new SyntaxError('Wrong number of arguments');
    }
    if (value !== false) {
        throw new Error('Assertion failed: Not false: ' + value);
    }
};


/**
 * Asserts that a value is NaN.
 *
 * @param value value to assert it's NaN
 * @throws {Error} Assertion failed.
 * @throws {SyntaxError} Wrong number of arguments.
 */
assert.NaN = function(value) {
    if (arguments.length != 1) {
        throw new SyntaxError('Wrong number of arguments');
    }
    if (!isNaN(value)) {
        throw new Error('Assertion failed: Not NaN: ' + value);
    }
};


/**
 * Asserts that two values are not identical.
 *
 * @param x first value to compare with
 * @param y second value to compare with
 * @throws {Error} Assertion failed.
 * @throws {SyntaxError} Wrong number of arguments.
 */
assert.notEquals = function(x, y) {
    if (arguments.length != 2) {
        throw new SyntaxError('Wrong number of arguments');
    }
    if (x === y) {
        throw new Error('Assertion failed: Identical: ' + x + ' === ' + y);
    }
};


/**
 * Asserts that a value is null.
 *
 * @param value value to assert it's null
 * @throws {Error} Assertion failed.
 * @throws {SyntaxError} Wrong number of arguments.
 */
assert.Null = function(value) {
    if (arguments.length != 1) {
        throw new SyntaxError('Wrong number of arguments');
    }
    if (value !== null) {
        throw new Error('Assertion failed: Not null: ' + value);
    }
};


/**
 * Asserts that a value is true.
 *
 * @param value value to assert it's true
 * @throws {Error} Assertion failed.
 * @throws {SyntaxError} Wrong number of arguments.
 */
assert.True = function(value) {
    if (arguments.length != 1) {
        throw new SyntaxError('Wrong number of arguments');
    }
    if (value !== true) {
        throw new Error('Assertion failed: Not true: ' + value);
    }
};


/**
 * Asserts that a value is undefined.
 *
 * @param value value to assert it's undefined
 * @throws {Error} Assertion failed.
 * @throws {SyntaxError} Wrong number of arguments.
 */
assert.Undefined = function(value) {
    if (arguments.length != 1) {
        throw new SyntaxError('Wrong number of arguments');
    }
    if (value !== undefined) {
        throw new Error('Assertion failed: Not undefined: ' + value);
    }
};
