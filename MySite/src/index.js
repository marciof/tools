(function () {
    'use strict';

    var module = angular.module('index', [
        'ngRoute',
        'usersPage'
    ]);

    module.config(['$routeProvider', function ($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: 'pages/usersPage.html',
                controller: 'usersPageController'
            })
            .otherwise({
                redirectTo: '/'
            });
    }]);
})();
