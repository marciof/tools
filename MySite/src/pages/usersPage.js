(function () {
    'use strict';

    var module = angular.module('usersPage', [
        'chart.js',
        'onErrorDirective',
        'logsApi',
        'usersApi'
    ]);

    module.controller('usersPageController', [
        '$q',
        '$scope',
        '$timeout',
        'logsApiLog',
        'logsApiLogAggregation',
        'usersApiUser',
        function ($q, $scope, $timeout, Log, LogAggregation, User) {

            $scope.users = User.query();
            $scope.logAggregation = new LogAggregation();

            $scope.userConversionsChartDataByUserId = {};
            $scope.userConversionsChartLabelsByUserId = {};
            $scope.userConversionsChartColors = ['#000000'];

            $scope.userConversionsChartOptions = {
                animation: false,
                bezierCurve: false,
                datasetFill: false,
                datasetStrokeWidth: 1,
                pointDot: false,
                scaleGridLineColor: 'black',
                scaleLineColor: 'black',
                scaleShowGridLines: false,
                scaleShowLabels: false,
                showScale: false,
                showTooltips: false
            };

            $q.all({
                users: $scope.users.$promise,
                logs: Log.query().$promise
            })
            .then(function (results) {
                return $scope.logAggregation.add(results.logs);
            })
            .then(function () {
                var index = 0;
                var CHART_BUILD_PAUSE_MILLIS = 50;

                $timeout(function buildUserChart() {
                    if (index < $scope.users.length) {
                        buildUserConversionsChart($scope.users[index++]);
                        $timeout(buildUserChart, CHART_BUILD_PAUSE_MILLIS);
                    }
                });
            });

            function buildUserConversionsChart(user) {
                var nrConversionsPerDay = $scope.logAggregation
                    .nrConversionsPerDayByUserId[user.id];

                if (nrConversionsPerDay) {
                    var dailyNrConversions = _.sortBy(nrConversionsPerDay,
                        function (nrConversions, day) {
                            return day;
                        });

                    $scope.userConversionsChartDataByUserId[user.id]
                        = [dailyNrConversions];

                    $scope.userConversionsChartLabelsByUserId[user.id]
                        = _.fill(new Array(dailyNrConversions.length), '');
                }
            }
        }
    ]);
})();
