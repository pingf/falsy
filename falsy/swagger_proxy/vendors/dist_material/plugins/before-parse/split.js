'use strict';

angular.module('sw.plugin.split', ['sw.plugins'])
    .factory('split', function ($q) {
        return {
            execute: execute
        };

        function execute (url, swagger) {
            var deferred = $q.defer();

            if (swagger && swagger.swagger && !swagger.tags) {
                var tags = {};

                angular.forEach(swagger.paths, function (path, key) {
                    var t = key.replace(/^\/?([^\/]+).*$/g, '$1');
                    tags[t] = true;

                    angular.forEach(path, function (method) {
                        if (!method.tags || !method.tags.length) {
                            method.tags = [t];
                        }
                    });
                });

                swagger.tags = [];

                Object.keys(tags).forEach(function (tag) {
                    swagger.tags.push({name: tag});
                });
            }

            deferred.resolve(true);

            return deferred.promise;
        }
    })
    .run(function (plugins, split) {
        plugins.add(plugins.BEFORE_PARSE, split);
    });
