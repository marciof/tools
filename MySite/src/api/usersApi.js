(function () {
    'use strict';

    var module = angular.module('usersApi', ['ngResource']);

    module.factory('usersApiUser', [
        '$resource',
        function ($resource) {

            var User = $resource('/api/users.json');

            User.prototype.disableAvatar = function () {
                this._isAvatarDisabled = true;
            };

            User.prototype.getFallbackAvatarText = function () {
                return this.getFirstNameLetter().toLocaleUpperCase();
            };

            User.prototype.getFirstNameLetter = function () {
                return (this.name.match(/\w/) || [''])[0];
            };

            User.prototype.hasAvatar = function () {
                return !this._isAvatarDisabled && !!this.avatar;
            };

            return User;
        }
    ]);
})();
