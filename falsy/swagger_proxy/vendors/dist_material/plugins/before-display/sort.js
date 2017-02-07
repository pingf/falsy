'use strict';

angular.module('sw.plugin.sort', ['sw.plugins'])
    .factory('sort', function ($q) {
        var order = {
            get: 1,
            head: 2,
            options: 3,
            post: 4,
            put: 5,
            patch: 6,
            delete: 7
        };

        return {
            execute: function (parseResult) {
                var deferred = $q.defer();

                angular.forEach(parseResult.resources, function (resource) {
                    resource.operations.sort(function (a, b) {
                        return (a.path.toLowerCase().replace(/[^a-z]+/gi, '') + '-' + (order[a.httpMethod] || 9))
                            .localeCompare(b.path.toLowerCase().replace(/[^a-z]+/gi, '') + '-' + (order[b.httpMethod] || 9));
                    });
                });

                deferred.resolve(true);

                return deferred.promise;
            }
        };
    })
    .run(function (plugins, sort) {
        plugins.add(plugins.BEFORE_DISPLAY, sort);
    });
