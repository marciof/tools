(function () {
    'use strict';

    var module = angular.module('registrationPage', [
        'mp.autoFocus',
        'ui.bootstrap'
    ]);

    module.factory('registrationPageTab', function () {

        function Tab(options) {
            this.isActive = _.get(options, 'isActive', false);
            this._isValid = _.get(options, 'isValid', null);
        }

        Tab.prototype.isValid = function () {
            return this._isValid ? this._isValid() : true;
        };

        return Tab;
    });

    module.controller('registrationPageController', [
        '$scope',
        'registrationPageTab',
        function ($scope, Tab) {

            var previousTab = null;
            var nextTab = null;

            $scope.input = {
                firstName: '',
                lastName: '',
                password: '',
                repeatPassword: '',
                wantsNewsletter: false,
                clockFormat: 24
            };

            $scope.nameTab = new Tab({
                isActive: true,
                isValid: function () {
                    return _.get($scope.form, 'firstName.$valid')
                        && _.get($scope.form, 'lastName.$valid');
                }
            });

            $scope.passwordTab = new Tab({
                isValid: function () {
                    return _.get($scope.form, 'password.$valid')
                        && _.get($scope.form, 'repeatPassword.$valid')
                        && ($scope.input.password === $scope.input.repeatPassword);
                }
            });

            $scope.preferencesTab = new Tab();
            $scope.reviewTab = new Tab();

            $scope.canRegister = function () {
                return $scope.nameTab.isValid()
                    && $scope.passwordTab.isValid()
                    && $scope.preferencesTab.isValid()
                    && $scope.reviewTab.isValid();
            };

            $scope.register = function () {
                alert('Good! :-)');
            };

            $scope.updateNavigation = function (newPreviousTab, newNextTab) {
                previousTab = newPreviousTab;
                nextTab = newNextTab;
            };

            $scope.goToNextTab = function () {
                if (nextTab) {
                    nextTab.isActive = true;
                }
            };

            $scope.goToPreviousTab = function () {
                if (previousTab) {
                    previousTab.isActive = true;
                }
            };
        }
    ]);
})();
