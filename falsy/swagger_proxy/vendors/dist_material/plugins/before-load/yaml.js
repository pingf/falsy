'use strict';

angular.module('sw.plugin.yaml', ['sw.plugins'])
    .factory('yaml', function ($q, $window) {
        return {
            execute: function (options) {
                var deferred = $q.defer();

                options.transformResponse = function (data, headersGetter) {
                    try {
                        return angular.fromJson(data);
                    } catch (ign) {
                        try {
                            var obj = $window.jsyaml.safeLoad(data);

                            headersGetter()['content-type'] = 'application/json';

                            return obj;
                        } catch (ign) {
                            return data;
                        }
                    }
                };

                deferred.resolve();

                return deferred.promise;
            }
        };
    })
    .run(function (plugins, yaml) {
        plugins.add(plugins.BEFORE_LOAD, yaml);
    });
