(function () {
    'use strict';

    var module = angular.module('onErrorDirective', []);
    var NG_SRC_PRIORITY = 99;

    module.directive('onError', function () {
        return {
            restrict: 'A',
            priority: NG_SRC_PRIORITY + 1,
            scope: {
                onError: '&'
            },
            link: function (scope, element) {
                element.bind('error', function () {
                    scope.onError();
                });
            }
        };
    });
})();
