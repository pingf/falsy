'use strict';

angular.module('sw.plugin.base', ['sw.plugins'])
    .factory('base', function ($q, $log) {
        return {
            execute: execute
        };

        function execute (url, swagger) {
            $log.debug('sw:plugin', 'base');

            var deferred = $q.defer();

            if (swagger && swagger.paths) {
                var parts = {};
                var min = Number.MAX_VALUE;

                angular.forEach(swagger.paths, function (path, key) {
                    parts[key] = key.split('/');

                    if (key[0] === '/') {
                        parts[key].shift();
                    }

                    min = Math.min(min, parts[key].length);
                });

                var paths = Object.keys(swagger.paths);
                var sames = [];

                for (var i = 0; i < min; i++) {
                    var first = parts[paths[0]][i];

                    if (/\{.+\}/.test(first) || (parts[paths[0]].length <= 1)) {
                        break;
                    }

                    var same = true;

                    for (var j = 0; j < paths.length; j++) {
                        if (parts[paths[j]][i] !== first) {
                            same = false;
                            break;
                        }
                    }

                    if (same) {
                        sames.push(first);
                    } else {
                        break;
                    }
                }

                if (sames.length > 0) {
                    var extracted = sames.join('/');

                    $log.debug('sw:plugin:base:extracted', extracted);

                    swagger.basePath = (swagger.basePath || '/');
                    swagger.basePath = swagger.basePath +
                        ((swagger.basePath[swagger.basePath.length - 1] === '/') ? '' : '/') + extracted;

                    angular.forEach(paths, function (path) {
                        swagger.paths['/' + parts[path].slice(sames.length).join('/')] = swagger.paths[path];
                        delete swagger.paths[path];
                    });
                }
            }

            deferred.resolve(true);

            return deferred.promise;
        }
    })
    .run(function (plugins, base) {
        plugins.add(plugins.BEFORE_PARSE, base);
    });
