'use strict';

angular.module('sw.plugin.auth', ['sw.plugins'])
    .factory('auth', function ($q/* , $window */) {
        return {
            execute: function (/* options */) {
                var deferred = $q.defer();

                /* Add auth key to params

                 options.params.auth_key = '...';
                 */

                /* Basic HTTP Authentication

                 var username = '...';
                 var password = '...';
                 var auth = $window.btoa(username + ':' + password);
                 options.headers['Authorization'] = 'Basic ' + auth;
                 */

                deferred.resolve();

                return deferred.promise;
            }
        };
    })
    .run(function (plugins, auth) {
        plugins.add(plugins.BEFORE_EXPLORER_LOAD, auth);
    });
