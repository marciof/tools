(function () {
    'use strict';

    var module = angular.module('index', [
        'ngRoute',
        'registrationPage'
    ]);

    module.config(['$routeProvider', function ($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: 'registrationPage/registrationPage.html',
                controller: 'registrationPageController'
            })
            .otherwise({
                redirectTo: '/'
            });
    }]);
})();
