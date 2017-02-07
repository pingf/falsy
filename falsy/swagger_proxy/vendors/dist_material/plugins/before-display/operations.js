'use strict';

angular.module('sw.plugin.operations', ['sw.plugins'])
    // List ungrouped operations
    .factory('operations', function ($q) {
        return {
            execute: function (parseResult) {
                var deferred = $q.defer();

                parseResult.info.operations = [];

                angular.forEach(parseResult.resources, function (resource) {
                    angular.forEach(resource.operations, function (operation) {
                        parseResult.info.operations.push(operation);
                    });

                    // TODO: allow configuration of minimum auto expanded endpoints
                    if (parseResult.resources.length <= 8) {
                        resource.open = true;
                    }
                });

                parseResult.info.operations.sort(function (a, b) {
                    return (a.path.toLowerCase().replace(/[^a-z]+/gi, '') + '-' + a.httpMethod)
                        .localeCompare(b.path.toLowerCase().replace(/[^a-z]+/gi, '') + '-' + b.httpMethod);
                });

                deferred.resolve();

                return deferred.promise;
            }
        };
    })
    .run(function (plugins, operations) {
        plugins.add(plugins.BEFORE_DISPLAY, operations);
    });
