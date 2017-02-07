/*
 * Orange angular-swagger-ui - v0.3.0
 *
 * (C) 2015 Orange, all right reserved
 * MIT Licensed
 */
'use strict';

angular
    .module('sw.plugins', []).factory('plugins', function ($q) {
        var modules = {};

        return {
            BEFORE_LOAD: 'BEFORE_LOAD',
            BEFORE_PARSE: 'BEFORE_PARSE',
            PARSE: 'PARSE',
            BEFORE_DISPLAY: 'BEFORE_DISPLAY',
            BEFORE_EXPLORER_LOAD: 'BEFORE_EXPLORER_LOAD',
            AFTER_EXPLORER_LOAD: 'AFTER_EXPLORER_LOAD',

            /**
             * Adds a new module to swagger-ui
             */
            add: function (phase, module) {
                if (!modules[phase]) {
                    modules[phase] = [];
                }
                if (modules[phase].indexOf(module) < 0) {
                    modules[phase].push(module);
                }
            },
            /**
             * Executes modules' phase
             */
            execute: function () {
                var args = Array.prototype.slice.call(arguments);
                var phase = args.splice(0, 1);
                var deferred = $q.defer();
                var phaseModules = modules[phase] || [];

                executeAll(deferred, [].concat(phaseModules), args);
                return deferred.promise;
            }
        };

        /**
         * Runs modules' "execute" function one by one
         */
        function executeAll (deferred, phaseModules, args, phaseExecuted) {
            var module = phaseModules.shift();
            if (module) {
                module
                    .execute.apply(module, args)
                    .then(function (executed) {
                        phaseExecuted = phaseExecuted || executed;
                        executeAll(deferred, phaseModules, args, phaseExecuted);
                    })
                    .catch(deferred.reject);
            } else {
                deferred.resolve(phaseExecuted);
            }
        }
    });
