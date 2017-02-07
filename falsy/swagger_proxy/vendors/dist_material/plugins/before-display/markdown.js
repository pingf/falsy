'use strict';

angular.module('sw.plugin.markdown', ['sw.plugins'])
    .factory('markdown', function ($q, $log, $window) {
        $log.debug('sw:plugin', 'markdown');

        var showdown = new $window.showdown.Converter({
            simplifiedAutoLink: true,
            tables: true,
            ghCodeBlocks: true,
            tasklists: true
        });

        return {
            execute: execute
        };

        function execute (parseResult) {
            $log.debug('sw:execute', 'markdown');

            var deferred = $q.defer();

            // TODO: is there any other GFM field to be transformed? Find "GFM" in http://swagger.io/specification/ page

            if (parseResult.info && parseResult.info.description) {
                parseResult.info.description = markdown(parseResult.info.description.replace(/^<br ?\/?>/i, ''));
            }

            angular.forEach(parseResult.securityDefinitions, function (sec) {
                var d = sec.description || '';

                // Obvious descriptions
                if (sec.type === 'apiKey' && d.toLowerCase() === 'API Key Authentication'.toLowerCase()) {
                    delete sec.description;
                } else if (sec.type === 'basic' && d.toLowerCase() === 'Basic HTTP Authentication'.toLowerCase()) {
                    delete sec.description;
                } else if (sec.type === 'oauth2' && d.toLowerCase() === 'OAuth 2.0 Authentication'.toLowerCase()) {
                    delete sec.description;
                } else {
                    sec.description = markdown(sec.description);
                }
            });

            angular.forEach(parseResult.resources, function (resource) {
                resource.description = markdown(resource.description);

                angular.forEach(resource.operations, function (operation) {
                    operation.description = markdown(operation.description);

                    // TODO: remove workaround? http://darosh.github.io/angular-swagger-ui-material/#?url=https:%2F%2Fapi.apis.guru%2Fspecs%2Fwinning.email%2F1.0.0%2Fswagger.json
                    operation.summary = operation.summary ? operation.summary.replace(/(<br>)+$/, '') : operation.summary;

                    angular.forEach(operation.responses, function (response) {
                        response.description = markdown(response.description);
                    });
                });
            });

            deferred.resolve();

            return deferred.promise;
        }

        function markdown (text) {
            return showdown.makeHtml(text || '');
        }
    })
    .run(function (plugins, markdown) {
        plugins.add(plugins.BEFORE_DISPLAY, markdown);
    });
