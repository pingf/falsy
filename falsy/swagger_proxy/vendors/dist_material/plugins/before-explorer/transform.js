'use strict';

angular.module('sw.plugin.transform', ['sw.plugins'])
    // Catch default transform invalid JSON parse
    .factory('transform', function ($q, $http) {
        return {
            execute: function (config) {
                var deferred = $q.defer();

                config.transformResponse = function (data, headersGetter, status) {
                    try {
                        return $http.defaults.transformResponse[0](data, headersGetter, status);
                    } catch (ing) {
                        return data;
                    }
                };

                deferred.resolve();

                return deferred.promise;
            }
        };
    })
    .run(function (plugins, transform) {
        plugins.add(plugins.BEFORE_EXPLORER_LOAD, transform);
    });
