(function () {
    'use strict';

    var module = angular.module('logsApi', ['ngResource']);

    module.constant('logsApiLogType', {
        CONVERSION: 'conversion',
        IMPRESSION: 'impression'
    });

    module.factory('logsApiLog', [
        '$resource',
        function ($resource) {
            return $resource('/api/logs.json');
        }
    ]);

    module.factory('logsApiLogAggregation', [
        '$q',
        '$timeout',
        'logsApiLogType',
        function ($q, $timeout, LogType) {

            var PROCESSING_CHUNK_TIME = 50;
            var PROCESSING_PAUSE_MILLIS = 100;

            function LogAggregation() {
                this.nrConversionsByUserId = {};
                this.nrConversionsPerDayByUserId = {};
                this.nrImpressionsByUserId = {};
                this.totalRevenueByUserId = {};
            }

            LogAggregation.prototype.add = function (logs) {
                var deferred = $q.defer();
                var index = 0;
                var that = this;

                $timeout(function processChunk() {
                    var startTime = Date.now();

                    while (index < logs.length) {
                        var log = logs[index++];

                        if (log.type === LogType.CONVERSION) {
                            that.addConversion(log);
                        }
                        else if (log.type === LogType.IMPRESSION) {
                            that.addImpression(log);
                        }

                        if ((Date.now() - startTime) >= PROCESSING_CHUNK_TIME) {
                            $timeout(processChunk, PROCESSING_PAUSE_MILLIS);
                            return;
                        }
                    }

                    deferred.resolve();
                });

                return deferred.promise;
            };

            LogAggregation.prototype.addConversion = function (log) {
                this.nrConversionsByUserId[log.user_id] =
                    (this.nrConversionsByUserId[log.user_id] || 0)
                    + 1;

                this.totalRevenueByUserId[log.user_id] =
                    (this.totalRevenueByUserId[log.user_id] || 0)
                    + log.revenue;

                var dateOnly = log.time.replace(/\s.*/, '');
                var nrConversionsPerDay
                    = this.nrConversionsPerDayByUserId[log.user_id];

                if (!nrConversionsPerDay) {
                    nrConversionsPerDay = {};
                    this.nrConversionsPerDayByUserId[log.user_id]
                        = nrConversionsPerDay;
                }

                nrConversionsPerDay[dateOnly] =
                    (nrConversionsPerDay[dateOnly] || 0)
                    + 1;
            };

            LogAggregation.prototype.addImpression = function (log) {
                this.nrImpressionsByUserId[log.user_id] =
                    (this.nrImpressionsByUserId[log.user_id] || 0)
                    + 1;
            };

            return LogAggregation;
        }
    ]);
})();
