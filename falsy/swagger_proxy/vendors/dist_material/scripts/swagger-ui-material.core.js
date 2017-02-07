'use strict';

angular.module('sw.ui.md',
    [
        'ngMaterial',
        'ngSanitize',
        'sw.ui',
        'sw.ui.directives'
    ]);

'use strict';

angular.module('sw.ui.md')
    .controller('ToolbarController', ["$scope", "$log", "$mdMedia", "data", "security", "theme", function ($scope, $log, $mdMedia, data, security, theme) {
        var vm = this;

        vm.data = data;
        vm.ui = data.ui;
        vm.search = null;
        vm.searchOpened = false;
        vm.editUrl = data.options.url;
        vm.loading = false;
        vm.$mdMedia = $mdMedia;

        vm.showSecurity = showSecurity;
        vm.showProxy = showProxy;
        vm.toggleGroups = toggleGroups;
        vm.editedUrl = editedUrl;
        vm.searchUpdated = searchUpdated;

        $scope.$on('sw:changed', update);

        update();

        function update () {
            $log.debug('sw:changed:toolbar');

            vm.loading = data.loading;
        }

        function editedUrl () {
            data.setUrl(vm.editUrl);
        }

        function searchUpdated () {
            $log.debug('sw:changed:search', vm.search);

            if (!vm.search) {
                data.model.search = {};
            } else {
                var trimmed = vm.search.toLowerCase().trim();
                var parts = trimmed.split(' ');
                var isMethod = ['get', 'post', 'put', 'patch', 'head', 'options', 'delete'].indexOf(parts[0]) > -1;
                var method = (parts.length > 1) ? parts[0] : (isMethod ? parts[0] : '');
                var path = (parts.length > 1) ? parts[1] : (isMethod ? '' : parts[0]);

                data.model.search = {httpMethod: method, path: path};
            }

            $log.debug('sw:changed:searching', data.model.search);
        }

        function toggleGroups (open) {
            angular.forEach(data.model.groups, function (group) {
                group.open = open;
            });
        }

        function showSecurity ($event) {
            security.showSecurity($event, data.swagger);
        }

        function showProxy ($event) {
            security.showProxy($event, data.swagger);
        }
    }]);

'use strict';

angular.module('sw.ui.md')
    .controller('MetaController', ["$scope", "$log", "data", "tools", "display", function ($scope, $log, data, tools, display) {
        var vm = this;

        $scope.$on('sw:changed', update);

        update();

        function update () {
            $log.debug('sw:changed:meta');

            vm.meta = data.model.info && display.meta(
                    data.model.info,
                    data.options.url,
                    data.options.validatorUrl,
                    tools.openFile
                );
        }
    }]);

'use strict';

angular.module('sw.ui.md')
    .controller('DetailController', ["$scope", "$rootScope", "$timeout", "$log", "data", "theme", "style", "tools", "utils", "syntax", "client", "format", function ($scope, $rootScope, $timeout, $log, data, theme, style, tools, utils, syntax, client, format) {
        var vm = this;

        vm.data = data;
        vm.theme = theme;
        vm.style = style;
        vm.utils = utils;
        vm.sop = null;
        vm.omg = false;
        vm.ngForm = {explorerForm: {}};
        vm.form = null;

        vm.submit = submit;
        vm.changed = changed;
        vm.openFile = tools.openFile;

        vm.dummy = $rootScope.$on('sw:operation', selectedOperation);

        var deregister;

        function selectedOperation () {
            if (deregister) {
                deregister();
            }

            var op = vm.sop = data.model.sop;

            vm.form = data.model.form[vm.sop.id];
            var opening = !data.ui.sidenavOpen;
            op.tab = op.tab || 0;

            // fixes tab content width flickering (might be angular-material issue)
            // and triggers .sum-fade animation
            vm.omg = !opening;

            $timeout(function () {
                data.ui.sidenavOpen = true;

                $timeout(function () {
                    vm.omg = false;
                }, 15);
            }, 150);

            if (op.responseClass && op.responseClass.schema && op.responseClass.schema.obj && !op.responseClass.schema.json) {
                op.responseClass.schema.json = syntax.json(angular.toJson(op.responseClass.schema.obj, true));
            }

            // TODO: this is fixing not selected single "text/html" in produces,
            // TODO: angular-swagger-ui probably setting this to "application/json" not present in op.produces
            if ((op.produces.indexOf(data.model.form[op.id].responseType)) === -1 && (op.produces.length === 1)) {
                data.model.form[op.id].responseType = op.produces[0];
            }

            op.responseArray = [];

            if (op.responseClass && op.responseClass.status) {
                op.responseArray.push({
                    code: op.responseClass.status,
                    description: op.responseClass.description || utils.statusInfo(op.responseClass.status)[0]
                });
            }

            angular.forEach(op.responses, function (r, c) {
                op.responseArray.push({
                    code: c,
                    description: r.description || utils.statusInfo(c)[0]
                });
            });

            op.responseArray.sort(function (a, b) {
                a.code.toString().localeCompare(b.code.toString());
            });

            deregister = $scope.$watch('vm.form', function () {
                changed(op);
            }, true);
        }

        function mockRequest (operation, done) {
            client.send(data.model.info, operation, data.model.form[operation.id], true)
                .then(done);
        }

        function changed (op) {
            mockRequest(op, function (options) {
                $log.debug('sw:mocked', options);

                op.mock = options;
            });
        }

        function submit (operation) {
            if (!vm.ngForm.explorerForm.$valid) {
                return;
            }

            $log.debug('sw:submit');

            operation.loading = true;

            client.send(data.model.info, operation, data.model.form[operation.id])
                .then(function (response) {
                    clientDone(operation, response);
                });
        }

        function clientDone (operation, response) {
            $log.debug('sw:response');

            operation.loading = false;
            operation.explorerResult = response;

            if (response && response.status) {
                response.statusString = response.status.toString();
            }

            response.fullUrl = format.fullUrl(response);
            response.body = angular.isObject(response.data) ? angular.toJson(response.data, true) : response.data;

            response.headerArray = [];

            if (response && response.headers) {
                angular.forEach(response.headers(), function (v, k) {
                    response.headerArray.push({
                        name: k,
                        value: v
                    });
                });

                response.headerArray.sort(function (a, b) {
                    a.name.localeCompare(b.name);
                });
            }

            var knownStatus = operation.responseArray.find(
                function (i) {
                    return i.code === response.status.toString();
                }
            );

            knownStatus = knownStatus || (response.statusText ? {description: response.statusText} : {});

            response.statusArray = [{
                code: response.status.toString(),
                description: knownStatus.description || utils.statusInfo(response.status)[0]
            }];

            $timeout(function () {
                operation.tab = 2;
            }, 50);
        }
    }]);

'use strict';

angular.module('sw.ui.md')
    .controller('DescriptionController', ["$scope", "$log", "data", function ($scope, $log, data) {
        var vm = this;

        $scope.$on('sw:changed', update);

        update();

        function update () {
            $log.debug('sw:changed:description');

            vm.description = data.model.info && data.model.info.description;
        }
    }]);

'use strict';

angular.module('sw.ui.md')
    .controller('ContentController', ["$rootScope", "data", "theme", function ($rootScope, data, theme) {
        var vm = this;

        vm.data = data;
        vm.theme = theme;

        vm.toggleGroup = toggleGroup;
        vm.selectOperation = selectOperation;

        function toggleGroup (group, $event) {
            $event.preventDefault();
            $event.stopPropagation();

            // Space bar does not stop propagation :-(
            if (($event.keyCode || $event.which) === 32) {
                return;
            }

            group.open = !group.open;
        }

        function selectOperation (op, $event) {
            $event.stopPropagation();
            data.model.sop = op;
            $rootScope.$emit('sw:operation');
        }
    }]);

/*
 * Orange angular-swagger-ui - v0.3.0
 *
 * (C) 2015 Orange, all right reserved
 * MIT Licensed
 */
'use strict';

angular.module('sw.plugin.parser', ['sw.plugins'])
    .factory('parser', ["$q", "$sce", "$location", "model", function ($q, $sce, $location, model) {
        var trustedSources;
        var operationId;
        var paramId;

        return {
            execute: execute
        };

        function execute (parserType, url, contentType, data, isTrustedSources, parseResult) {
            var deferred = $q.defer();
            if (data.swagger === '2.0' && (parserType === 'json' || (parserType === 'auto' && contentType === 'application/json'))) {
                trustedSources = isTrustedSources;
                try {
                    parseSwagger2Json(data, url, deferred, parseResult);
                } catch (e) {
                    deferred.reject({
                        message: 'failed to parse swagger: ' + e.message
                    });
                }
            } else {
                deferred.resolve(false);
            }
            return deferred.promise;
        }

        /**
         * parse swagger description to ease HTML generation
         */
        function parseSwagger2Json (swagger, url, deferred, parseResult) {
            var map = {};
            var form = {};
            var resources = [];
            var info = swagger.info;
            var openPath = $location.hash();
            var defaultContentType = 'application/json';

            operationId = 0;
            paramId = 0;
            parseInfo(swagger, url, info, defaultContentType);
            parseTags(swagger, resources, map);
            parseOperations(swagger, resources, form, map, defaultContentType, openPath);
            cleanUp(resources, openPath);
            // prepare result
            parseResult.info = info;
            parseResult.resources = resources;
            parseResult.form = form;
            parseResult.securityDefinitions = angular.copy(swagger.securityDefinitions);
            deferred.resolve(true);
        }

        /**
         * parse main info
         */
        function parseInfo (swagger, url, info, defaultContentType) {
            // build URL params
            var a = angular.element('<a href="' + url + '"></a>')[0];
            swagger.schemes = swagger.schemes || [];
            swagger.schemes.sort();
            swagger.schemes.reverse();
            swagger.schemes = [swagger.schemes && swagger.schemes[0] || a.protocol.replace(':', '')];
            swagger.host = swagger.host || a.host;
            swagger.consumes = swagger.consumes || [defaultContentType];
            swagger.produces = swagger.produces || [defaultContentType];
            // build main info
            info.scheme = swagger.schemes[0];
            info.basePath = swagger.basePath;
            info.host = swagger.host;
            info.description = trustHtml(info.description);
            info.externalDocs = swagger.externalDocs;
        }

        /**
         * parse tags
         */
        function parseTags (swagger, resources, map) {
            var i, l, tag;
            if (!swagger.tags) {
                resources.push({
                    name: 'default',
                    open: true
                });
                map['default'] = 0;
            } else {
                for (i = 0, l = swagger.tags.length; i < l; i++) {
                    tag = swagger.tags[i];
                    resources.push(tag);
                    map[tag.name] = i;
                }
            }
        }

        /**
         * parse operations
         */
        function parseOperations (swagger, resources, form, map, defaultContentType, openPath) {
            var pathParameters;
            var tag;
            var resource;

            angular.forEach(swagger.paths, function (pathObject, path) {
                pathParameters = pathObject.parameters || [];
                delete pathObject.parameters;

                angular.forEach(pathObject, function (operation, httpMethod) {
                    // TODO manage 'deprecated' operations ?
                    operation.id = operationId;
                    operation.description = trustHtml(operation.description);
                    operation.produces = operation.produces || swagger.produces;
                    form[operationId] = {
                        responseType: defaultContentType
                    };
                    operation.httpMethod = httpMethod;
                    operation.path = path;
                    parseParameters(swagger, operation, pathParameters, form, defaultContentType);
                    parseResponses(swagger, operation);
                    operation.tags = operation.tags || ['default'];
                    // map operation to resource
                    tag = operation.tags[0];
                    if (angular.isUndefined(map[tag])) {
                        map[tag] = resources.length;
                        resources.push({
                            name: tag
                        });
                    }
                    resource = resources[map[operation.tags[0]]];
                    operation.open = openPath && openPath === operation.operationId || openPath === resource.name + '*';
                    resource.operations = resource.operations || [];
                    resource.operations.push(operation);
                    if (operation.open) {
                        resource.open = true;
                    }
                    operationId++;
                });
            });
        }

        /**
         * compute path and operation parameters
         */
        function computeParameters (swagger, pathParameters, operation) {
            var i;
            var j;
            var k;
            var l;
            var operationParameters = operation.parameters || [];
            var parameters = [].concat(operationParameters);
            var found;
            var pathParameter;
            var operationParameter;

            for (i = 0, l = pathParameters.length; i < l; i++) {
                found = false;
                pathParameter = model.resolveReference(swagger, pathParameters[i]);

                for (j = 0, k = operationParameters.length; j < k; j++) {
                    operationParameter = model.resolveReference(swagger, operationParameters[j]);
                    if (pathParameter.name === operationParameter.name && pathParameter.in === operationParameter.in) {
                        // overridden parameter
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    // add path parameter to operation ones
                    parameters.push(pathParameter);
                }
            }
            return parameters;
        }

        /**
         * parse operation parameters
         */
        function parseParameters (swagger, operation, pathParameters, form, defaultContentType) {
            var i;
            var l;
            var param;
            var parameters = operation.parameters = computeParameters(swagger, pathParameters, operation);

            for (i = 0, l = parameters.length; i < l; i++) {
                // TODO manage 'collectionFormat' (csv, multi etc.) ?
                // TODO manage constraints (pattern, min, max etc.) ?
                param = parameters[i] = model.resolveReference(swagger, parameters[i]);
                param.id = paramId;
                param.type = model.getType(param);
                param.description = trustHtml(param.description);
                if (param.items && param.items.enum) {
                    param.enum = param.items.enum;
                    param.default = param.items.default;
                }
                param.subtype = param.enum ? 'enum' : param.type;
                // put param into form scope
                form[operationId][param.name] = param.default || '';
                if (param.schema) {
                    param.schema.display = 1; // display schema
                    param.schema.json = model.generateSampleJson(swagger, param.schema);
                    param.schema.model = $sce.trustAsHtml(model.generateModel(swagger, param.schema));
                }
                if (param.in === 'body' || param.in === 'formData') {
                    operation.consumes = operation.consumes || swagger.consumes;
                    form[operationId].contentType = operation.consumes.length === 1 ? operation.consumes[0] : defaultContentType;
                }
                paramId++;
            }
        }

        /**
         * parse operation responses
         */
        function parseResponses (swagger, operation) {
            // var sampleJson;
            var sampleObj;

            if (operation.responses) {
                angular.forEach(operation.responses, function (response, code) {
                    // TODO manage response headers
                    response.description = trustHtml(response.description);

                    if (response.schema) {
                        if (response.examples && response.examples[operation.produces[0]]) {
                            // TODO: we prefer object(?)
                            // sampleJson = angular.toJson(response.examples[operation.produces[0]], true);
                            sampleObj = response.examples[operation.produces[0]];
                        } else {
                            // sampleJson = model.generateSampleJson(swagger, response.schema);
                            sampleObj = model.getSampleObj(swagger, response.schema);
                        }

                        // response.schema.json = sampleJson;
                        response.schema.obj = sampleObj;

                        if (response.schema.type === 'object' || response.schema.type === 'array' || response.schema.$ref) {
                            response.display = 1; // display schema
                            response.schema.model = $sce.trustAsHtml(model.generateModel(swagger, response.schema));
                        } else if (response.schema.type === 'string') {
                            delete response.schema;
                        }

                        if (code === '200' || code === '201') {
                            operation.responseClass = response;
                            operation.responseClass.display = 1;
                            operation.responseClass.status = code;
                            delete operation.responses[code];
                        } else {
                            operation.hasResponses = true;
                        }
                    } else {
                        operation.hasResponses = true;
                    }
                });
            }
        }

        function cleanUp (resources, openPath) {
            var i;
            var resource;
            var operations;

            for (i = 0; i < resources.length; i++) {
                resource = resources[i];
                operations = resources[i].operations;
                resource.open = resource.open || openPath === resource.name || openPath === resource.name + '*';
                if (!operations || (operations && operations.length === 0)) {
                    resources.splice(i--, 1);
                }
            }

            // sort resources alphabetically
            resources.sort(function (a, b) {
                if (a.name > b.name) {
                    return 1;
                } else if (a.name < b.name) {
                    return -1;
                }
                return 0;
            });

            model.clearCache();
        }

        function trustHtml (text) {
            var trusted = text;

            if (angular.isString(text) && trustedSources) {
                trusted = $sce.trustAsHtml(escapeChars(text));
            }

            // else ngSanitize MUST be added to app
            return trusted;
        }

        function escapeChars (text) {
            return text
                .replace(/&/g, '&amp;')
                .replace(/<([^\/a-zA-Z])/g, '&lt;$1')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
    }])
    .run(["plugins", "parser", function (plugins, parser) {
        plugins.add(plugins.PARSE, parser);
    }]);

'use strict';

angular.module('sw.ui.md')
    .factory('utils', ["dialog", "theme", "httpData", function (dialog, theme, httpData) {
        return {
            method: method,
            status: status,
            header: header,
            statusInfo: statusInfo
        };

        function method (method, $event) {
            var i = httpData.method[method];

            dialog.show($event, {
                title: method.toUpperCase(),
                subtitle: 'HTTP Method',
                header: null,
                description: i[0],
                link: i[2],
                section: rfc(i[1]),
                style: theme[method],
                meta: [i[3], i[4], i[5]]
            });
        }

        function status (code, $event) {
            var i = statusInfo(code);

            dialog.show($event, {
                title: code,
                subtitle: 'HTTP Status',
                header: i[0],
                description: i[1],
                link: i[3],
                section: rfc(i[2]),
                style: theme[code[0]] || theme[7],
                meta: null
            });
        }

        function header (title, $event) {
            var i = httpData.header[title.toLowerCase()] || [title, 'Unknown header.', '', null];

            dialog.show($event, {
                title: i[0],
                subtitle: 'HTTP Header',
                header: null,
                description: i[1],
                link: i[3],
                section: rfc(i[2]),
                style: theme[i[1]] || theme.undefined,
                meta: null
            });
        }

        function rfc (section) {
            return section.replace(/(RFC)(.*)(#)(.*)/i, '$1 $2 – $4');
        }

        function statusInfo (code) {
            return httpData.status[code] || httpData.status[code[0] + 'xx'] ||
                ['**Undefined**', 'no spec found.', '', null];
        }
    }]);

'use strict';

angular.module('sw.ui.md')
    .factory('tools', ["$window", "data", function ($window, data) {
        return {
            openFile: openFile
        };

        function openFile ($event, isSwagger) {
            var text;
            var type;

            if (isSwagger) {
                // TODO: fromJson is lazy fix for https://github.com/crucialfelix/supercolliderjs/issues/17
                var json = angular.toJson(data.swagger, true);

                text = (isSwagger === 'swagger.json')
                    ? json : $window.jsyaml.safeDump(angular.fromJson(json));
                type = (isSwagger === 'swagger.json') ? 'application/json' : 'text/yaml';
            } else {
                text = data.model.sop.explorerResult.body;
                type = data.model.sop.explorerResult.headers('content-type') || 'text/plain';
            }

            // noinspection JSUnresolvedFunction
            var out = new $window.Blob([text], {type: type});

            // noinspection JSUnresolvedFunction
            $event.target.href = $window.URL.createObjectURL(out);
        }
    }]);

'use strict';

angular.module('sw.ui.md')
    .factory('theme', function () {
        var defaults = {
            get: 'md-primary',
            head: 'md-primary md-hue-2',
            options: 'md-primary md-hue-3',
            post: 'md-accent',
            put: 'md-accent md-hue-2',
            patch: 'md-accent md-hue-2',
            delete: 'md-warn',
            1: 'md-accent',
            2: 'md-primary',
            3: 'md-accent md-hue-2',
            4: 'md-warn',
            5: 'md-warn',
            7: 'md-warn',
            standard: 'md-accent',
            obsoleted: 'md-warn',
            undefined: 'md-accent',
            key: '',
            string: 'md-primary',
            number: 'md-warn',
            boolean: 'md-accent md-hue-3',
            null: 'md-accent md-hue-2'
        };

        var self = {
            $configure: configure
        };

        angular.extend(self, defaults);

        return self;

        function configure (theme) {
            angular.extend(self, defaults);
            angular.extend(self, theme || {});

            return self;
        }
    });

/*
 * Orange angular-swagger-ui - v0.3.0
 *
 * (C) 2015 Orange, all right reserved
 * MIT Licensed
 */
'use strict';

angular.module('sw.ui.md')
    .factory('syntax', ["theme", function (theme) {
        var prefix = 'md-button ';

        return {
            json: json
        };

        // from http://stackoverflow.com/questions/4810841/how-can-i-pretty-print-json-using-javascript
        function json (json) {
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
                var cls = prefix + theme.number;

                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = prefix + theme.key;
                    } else {
                        cls = prefix + theme.string;
                    }
                } else if (/true|false/.test(match)) {
                    cls = prefix + theme.boolean;
                } else if (/null/.test(match)) {
                    cls = prefix + theme.null;
                }

                return '<span class="' + cls + '">' + match + '</span>';
            });
        }
    }]);

'use strict';

angular.module('sw.ui.md')
    .factory('style', ["theme", "httpData", function (theme, httpData) {
        return {
            header: header
        };

        function header (title) {
            var i = httpData.header[title.toLowerCase()];

            if (i) {
                return theme[i[1]] || theme.undefined;
            } else {
                return null;
            }
        }
    }]);

'use strict';

angular.module('sw.ui.md')
    .factory('security', ["$q", "$http", "$timeout", "$interval", "$window", "$rootScope", "dialog", "data", function ($q, $http, $timeout, $interval, $window, $rootScope, dialog, data) {
        var storage = $window.sessionStorage;
        var securityDefinitions;
        var credentials;
        var host;
        var config;
        var configPromise = $http({
            method: 'GET',
            url: './auth.json'
        }).then(function (response) {
            config = response.data;
        });

        var deReg = $rootScope.$on('sw:changed', setSwagger);

        $rootScope.$on('$destroy', function () {
            deReg();
        });

        return {
            execute: execute,
            showSecurity: showSecurity,
            showProxy: showProxy
        };

        function setSwagger () {
            if (!data.swagger) {
                host = null;
                securityDefinitions = null;
                credentials = null;
            } else {
                host = data.swagger.host;
                securityDefinitions = data.model.securityDefinitions;
                configPromise.then(init);
            }
        }

        function init () {
            var stored = storage.getItem('swaggerUiSecurity:' + host);
            credentials = stored ? angular.fromJson(stored) : {};

            angular.forEach(securityDefinitions, function (sec, name) {
                if (sec.type === 'apiKey') {
                    credentials[name] = credentials[name] || '';
                } else if (sec.type === 'basic') {
                    credentials[name] = credentials[name] || {username: '', password: ''};
                } else if (sec.type === 'oauth2') {
                    sec.scopeKey = getScopeKey(name, sec);

                    if (config[host] && config[host]['oauth2']) {
                        var cid = config[host]['oauth2'].clientId;
                    }

                    credentials[sec.scopeKey] = credentials[sec.scopeKey] ||
                        {
                            clientId: cid || '',
                            accessToken: '',
                            tokenType: '',
                            expiresIn: null,
                            expiresFrom: null,
                            scopes: initScopes(sec)
                        };
                }
            });
        }

        function saveCredentials () {
            storage.setItem('swaggerUiSecurity:' + host, angular.toJson(credentials));
        }

        function execute (options) {
            var deferred = $q.defer();

            if (data.options.proxy) {
                options.url = data.options.proxy + options.url;
            }

            angular.forEach(securityDefinitions, function (sec, name) {
                if (sec.type === 'apiKey') {
                    if (sec.in === 'header') {
                        options.headers[sec.name] = credentials[name].apiKey;
                    } else if (sec.in === 'query') {
                        options.params[sec.name] = credentials[name].apiKey;
                    }
                } else if (sec.type === 'basic') {
                    var username = credentials[name].username;
                    var password = credentials[name].password;
                    var auth = $window.btoa(username + ':' + password);
                    options.headers['Authorization'] = 'Basic ' + auth;
                } else if (sec.type === 'oauth2') {
                    var c = credentials[sec.scopeKey];

                    if (c.accessToken) {
                        var a = [];

                        if (c.tokenType) {
                            a.push(c.tokenType);
                        }

                        a.push(c.accessToken);

                        options.headers['Authorization'] = a.join(' ');
                    }
                }
            });

            deferred.resolve();

            return deferred.promise;
        }

        function getScopeKey (name, sec) {
            var scopes = [];

            angular.forEach(sec.scopes, function (v, k) {
                scopes.push(k);
            });

            return name + ':' + hashCode(scopes.join(' '));
        }

        function initScopes (sec) {
            var obj = {};

            angular.forEach(sec.scopes, function (v, k) {
                obj[k] = true;
            });

            return obj;
        }

        function getSelectedScopes (sec) {
            var s = [];

            angular.forEach(credentials[sec.scopeKey].scopes, function (v, k) {
                if (v) {
                    s.push(k);
                }
            });

            return s.join('+');
        }

        // from http://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
        function hashCode (text) {
            var hash = 0;

            if (text.length === 0) {
                return hash;
            }

            for (var i = 0; i < text.length; i++) {
                var character = text.charCodeAt(i);

                hash = ((hash << 5) - hash) + character;
                hash = (hash & hash) + 0x80000000;
            }

            return hash.toString(16);
        }

        function showSecurity ($event) {
            configPromise.then(
                function () {
                    showInternal($event);
                },
                function () {
                    showInternal($event);
                }
            );
        }

        function showProxy ($event) {
            dialog.show($event, {
                options: data.options
            }, 'proxy');
        }

        function showInternal ($event) {
            var locals = {
                security: securityDefinitions,
                credentials: credentials,
                singleSecurity: Object.keys(securityDefinitions || {}).length === 1
            };

            var toBeDestroyed = $rootScope.$watch(function () {
                return credentials;
            }, saveCredentials, true);

            angular.forEach(securityDefinitions,
                function (sec) {
                    if (sec.type === 'apiKey') {
                    } else if (sec.type === 'basic') {
                    } else if (sec.type === 'oauth2') {
                        var redirectUrl = $window.location.href.replace($window.location.hash, '') + 'auth.html';
                        sec.friendlyScopes = friendlyScopes(sec);
                        sec.link = '#';

                        counter(sec, locals);

                        sec.clicked = function ($event) {
                            $event.preventDefault();
                            var clientId = encodeURIComponent(credentials[sec.scopeKey].clientId || '');

                            sec.link = sec.authorizationUrl +
                                '?response_type=token' +
                                (clientId ? ('&client_id=' + clientId) : '') +
                                '&scope=' + getSelectedScopes(sec) +
                                '&redirect_uri=' + redirectUrl;

                            $window.open(sec.link);

                            $window.onOAuthFinished = function (qp) {
                                // using $timeout as $apply in non-Angular event
                                $timeout(function () {
                                    if (qp.code) {
                                        $http({
                                            method: 'POST',
                                            url: sec.tokenUrl,
                                            headers: {
                                                Accept: 'application/json'
                                            },
                                            params: {
                                                grant_type: 'authorization_code',
                                                code: qp.code,
                                                redirect_url: redirectUrl,
                                                client_id: clientId,
                                                client_secret: config[host]['oauth2'].clientSecret
                                            }
                                        }).then(function (response) {
                                            var qp = response.data;

                                            angular.extend(credentials[sec.scopeKey], {
                                                accessToken: qp['access_token'],
                                                tokenType: qp['token_type'],
                                                expiresIn: parseInt(qp['expires_in']),
                                                expiresFrom: Date.now()
                                            });
                                        });
                                    } else {
                                        angular.extend(credentials[sec.scopeKey], {
                                            accessToken: qp['access_token'],
                                            tokenType: qp['token_type'],
                                            expiresIn: parseInt(qp['expires_in']),
                                            expiresFrom: Date.now()
                                        });
                                    }
                                });
                            };
                        };
                    }
                }
            );

            dialog.show($event, locals, 'security').then(function () {
                toBeDestroyed();
            });
        }

        function friendlyScopes (sec) {
            var obj = {};

            angular.forEach(sec.scopes, function (v, k) {
                obj[k] = k.replace(/^.*\/([^\/]+)$/g, '$1') || k;
            });

            return obj;
        }

        function counter (sec, locals) {
            var c = credentials[sec.scopeKey];

            if (c.expiresIn) {
                sec.counter = Math.round((c.expiresFrom + c.expiresIn * 1000 - Date.now()) / 1000) + ' seconds';
            }

            var promise = $interval(function () {
                if (!locals.opened) {
                    $interval.cancel(promise);
                }

                if (c.expiresIn) {
                    sec.counter = Math.round((c.expiresFrom + c.expiresIn * 1000 - Date.now()) / 1000) + ' seconds';
                }
            }, 1000);
        }
    }])
    .run(["plugins", "security", function (plugins, security) {
        plugins.add(plugins.BEFORE_EXPLORER_LOAD, security);
    }]);

'use strict';

// noinspection HtmlDeprecatedTag
angular.module('sw.ui.md')
    .value('httpData', {
        method: {
            delete: [
                'requests that the origin server remove the association between the target resource and its current functionality.',
                'RFC7231#4.3.5',
                'http://tools.ietf.org/html/rfc7231#section-4.3.5',
                false,
                true,
                false
            ],
            get: [
                'requests transfer of a current selected representation for the target resource.',
                'RFC7231#4.3.1',
                'http://tools.ietf.org/html/rfc7231#section-4.3.1',
                true,
                true,
                true
            ],
            head: [
                'is identical to GET except that the server MUST NOT send a message body in the response (i.e., the response terminates at the end of the header block).',
                'RFC7231#4.3.2',
                'http://tools.ietf.org/html/rfc7231#section-4.3.2',
                true,
                true,
                true
            ],
            options: [
                'requests information about the communication options available on the request/response chain identified by the effective request URI.',
                'RFC7231#4.3.7',
                'http://tools.ietf.org/html/rfc7231#section-4.3.7',
                true,
                true,
                false
            ],
            post: [
                'requests that the target resource process the representation enclosed in the request according to the resource\'s own specific semantics.',
                'RFC7231#4.3.3',
                'http://tools.ietf.org/html/rfc7231#section-4.3.3',
                false,
                false,
                false
            ],
            put: [
                'requests that the state of the target resource be created or replaced with the state defined by the representation enclosed in the request message payload.',
                'RFC7231#4.3.4',
                'http://tools.ietf.org/html/rfc7231#section-4.3.4',
                false,
                true,
                false
            ],
            patch: [
                'requests that a set of changes described in the request entity be applied to the resource identified by the Request-URI.',
                'RFC5789',
                'http://tools.ietf.org/html/rfc5789#section-2',
                false,
                false,
                false
            ]
        },
        status: {
            100: [
                'Continue',
                'indicates that the initial part of a request has been received and has not yet been rejected by the server.',
                'RFC7231#6.2.1',
                'http://tools.ietf.org/html/rfc7231#section-6.2.1'
            ],
            101: [
                'Switching Protocols',
                'indicates that the server understands and is willing to comply with the client\'s request, via the Upgrade header field, for a change in the application protocol being used on this connection.',
                'RFC7231#6.2.2',
                'http://tools.ietf.org/html/rfc7231#section-6.2.2'
            ],
            102: [
                'Processing',
                'is an interim response used to inform the client that the server has accepted the complete request, but has not yet completed it.',
                'RFC5218#10.1',
                'http://tools.ietf.org/html/rfc2518#section-10.1'
            ],
            200: [
                'OK',
                'indicates that the request has succeeded.',
                'RFC7231#6.3.1',
                'http://tools.ietf.org/html/rfc7231#section-6.3.1'
            ],
            201: [
                'Created',
                'indicates that the request has been fulfilled and has resulted in one or more new resources being created.',
                'RFC7231#6.3.2',
                'http://tools.ietf.org/html/rfc7231#section-6.3.2'
            ],
            202: [
                'Accepted',
                'indicates that the request has been accepted for processing, but the processing has not been completed.',
                'RFC7231#6.3.3',
                'http://tools.ietf.org/html/rfc7231#section-6.3.3'
            ],
            203: [
                'Non-Authoritative Information',
                'indicates that the request was successful but the enclosed payload has been modified from that of the origin server\'s 200 (OK) response by a transforming proxy.',
                'RFC7231#6.3.4',
                'http://tools.ietf.org/html/rfc7231#section-6.3.4'
            ],
            204: [
                'No Content',
                'indicates that the server has successfully fulfilled the request and that there is no additional content to send in the response payload body.',
                'RFC7231#6.3.5',
                'http://tools.ietf.org/html/rfc7231#section-6.3.5'
            ],
            205: [
                'Reset Content',
                'indicates that the server has fulfilled the request and desires that the user agent reset the \"document view\", which caused the request to be sent, to its original state as received from the origin server.',
                'RFC7231#6.3.6',
                'http://tools.ietf.org/html/rfc7231#section-6.3.6'
            ],
            206: [
                'Partial Content',
                'indicates that the server is successfully fulfilling a range request for the target resource by transferring one or more parts of the selected representation that correspond to the satisfiable ranges found in the requests\'s Range header field.',
                'RFC7233#4.1',
                'http://tools.ietf.org/html/rfc7233#section-4.1'
            ],
            207: [
                'Multi-Status',
                'provides status for multiple independent operations.',
                'RFC5218#10.2',
                'http://tools.ietf.org/html/rfc2518#section-10.2'
            ],
            226: [
                'IM Used',
                'The server has fulfilled a GET request for the resource, and the response is a representation of the result of one or more instance-manipulations applied to the current instance.',
                'RFC3229#10.4.1',
                'http://tools.ietf.org/html/rfc3229#section-10.4.1'
            ],
            300: [
                'Multiple Choices',
                'indicates that the target resource has more than one representation, each with its own more specific identifier, and information about the alternatives is being provided so that the user (or user agent) can select a preferred representation by redirecting its request to one or more of those identifiers.',
                'RFC7231#6.4.1',
                'http://tools.ietf.org/html/rfc7231#section-6.4.1'
            ],
            301: [
                'Moved Permanently',
                'indicates that the target resource has been assigned a new permanent URI and any future references to this resource ought to use one of the enclosed URIs.',
                'RFC7231#6.4.2',
                'http://tools.ietf.org/html/rfc7231#section-6.4.2'
            ],
            302: [
                'Found',
                'indicates that the target resource resides temporarily under a different URI.',
                'RFC7231#6.4.3',
                'http://tools.ietf.org/html/rfc7231#section-6.4.3'
            ],
            303: [
                'See Other',
                'indicates that the server is redirecting the user agent to a different resource, as indicated by a URI in the Location header field, that is intended to provide an indirect response to the original request.',
                'RFC7231#6.4.4',
                'http://tools.ietf.org/html/rfc7231#section-6.4.4'
            ],
            304: [
                'Not Modified',
                'indicates that a conditional GET request has been received and would have resulted in a 200 (OK) response if it were not for the fact that the condition has evaluated to false.',
                'RFC7232#4.1',
                'http://tools.ietf.org/html/rfc7232#section-4.1'
            ],
            305: [
                'Use Proxy',
                '*deprecated*',
                'RFC7231#6.4.5',
                'http://tools.ietf.org/html/rfc7231#section-6.4.5'
            ],
            307: [
                'Temporary Redirect',
                'indicates that the target resource resides temporarily under a different URI and the user agent MUST NOT change the request method if it performs an automatic redirection to that URI.',
                'RFC7231#6.4.7',
                'http://tools.ietf.org/html/rfc7231#section-6.4.7'
            ],
            308: [
                'Permanent Redirect',
                'The target resource has been assigned a new permanent URI and any future references to this resource SHOULD use one of the returned URIs. [...] This status code is similar to 301 Moved Permanently (Section 7.3.2 of rfc7231), except that it does not allow rewriting the request method from POST to GET.',
                'RFC7238',
                'http://tools.ietf.org/html/rfc7238'
            ],
            400: [
                'Bad Request',
                'indicates that the server cannot or will not process the request because the received syntax is invalid, nonsensical, or exceeds some limitation on what the server is willing to process.',
                'RFC7231#6.5.1',
                'http://tools.ietf.org/html/rfc7231#section-6.5.1'
            ],
            401: [
                'Unauthorized',
                'indicates that the request has not been applied because it lacks valid authentication credentials for the target resource.',
                'RFC7235#6.3.1',
                'http://tools.ietf.org/html/rfc7235#section-3.1'
            ],
            402: [
                'Payment Required',
                '*reserved*',
                'RFC7231#6.5.2',
                'http://tools.ietf.org/html/rfc7231#section-6.5.2'
            ],
            403: [
                'Forbidden',
                'indicates that the server understood the request but refuses to authorize it.',
                'RFC7231#6.5.3',
                'http://tools.ietf.org/html/rfc7231#section-6.5.3'
            ],
            404: [
                'Not Found',
                'indicates that the origin server did not find a current representation for the target resource or is not willing to disclose that one exists.',
                'RFC7231#6.5.4',
                'http://tools.ietf.org/html/rfc7231#section-6.5.4'
            ],
            405: [
                'Method Not Allowed',
                'indicates that the method specified in the request-line is known by the origin server but not supported by the target resource.',
                'RFC7231#6.5.5',
                'http://tools.ietf.org/html/rfc7231#section-6.5.5'
            ],
            406: [
                'Not Acceptable',
                'indicates that the target resource does not have a current representation that would be acceptable to the user agent, according to the proactive negotiation header fields received in the request, and the server is unwilling to supply a default representation.',
                'RFC7231#6.5.6',
                'http://tools.ietf.org/html/rfc7231#section-6.5.6'
            ],
            407: [
                'Proxy Authentication Required',
                'is similar to 401 (Unauthorized), but indicates that the client needs to authenticate itself in order to use a proxy.',
                'RFC7231#6.3.2',
                'http://tools.ietf.org/html/rfc7231#section-6.3.2'
            ],
            408: [
                'Request Timeout',
                'indicates that the server did not receive a complete request message within the time that it was prepared to wait.',
                'RFC7231#6.5.7',
                'http://tools.ietf.org/html/rfc7231#section-6.5.7'
            ],
            409: [
                'Conflict',
                'indicates that the request could not be completed due to a conflict with the current state of the resource.',
                'RFC7231#6.5.8',
                'http://tools.ietf.org/html/rfc7231#section-6.5.8'
            ],
            410: [
                'Gone',
                'indicates that access to the target resource is no longer available at the origin server and that this condition is likely to be permanent.',
                'RFC7231#6.5.9',
                'http://tools.ietf.org/html/rfc7231#section-6.5.9'
            ],
            411: [
                'Length Required',
                'indicates that the server refuses to accept the request without a defined Content-Length.',
                'RFC7231#6.5.10',
                'http://tools.ietf.org/html/rfc7231#section-6.5.10'
            ],
            412: [
                'Precondition Failed',
                'indicates that one or more preconditions given in the request header fields evaluated to false when tested on the server.',
                'RFC7232#4.2',
                'http://tools.ietf.org/html/rfc7232#section-4.2'
            ],
            413: [
                'Payload Too Large',
                'indicates that the server is refusing to process a request because the request payload is larger than the server is willing or able to process.',
                'RFC7231#6.5.11',
                'http://tools.ietf.org/html/rfc7231#section-6.5.11'
            ],
            414: [
                'URI Too Long',
                'indicates that the server is refusing to service the request because the request-target is longer than the server is willing to interpret.',
                'RFC7231#6.5.12',
                'http://tools.ietf.org/html/rfc7231#section-6.5.12'
            ],
            415: [
                'Unsupported Media Type',
                'indicates that the origin server is refusing to service the request because the payload is in a format not supported by the target resource for this method.',
                'RFC7231#6.5.13',
                'http://tools.ietf.org/html/rfc7231#section-6.5.13'
            ],
            416: [
                'Range Not Satisfiable',
                'indicates that none of the ranges in the request\'s Range header field overlap the current extent of the selected resource or that the set of ranges requested has been rejected due to invalid ranges or an excessive request of small or overlapping ranges.',
                'RFC7233#4.4',
                'http://tools.ietf.org/html/rfc7233#section-4.4'
            ],
            417: [
                'Expectation Failed',
                'indicates that the expectation given in the request\'s Expect header field could not be met by at least one of the inbound servers.',
                'RFC7231#6.5.14',
                'http://tools.ietf.org/html/rfc7231#section-6.5.14'
            ],
            422: [
                'Unprocessable Entity',
                'means the server understands the content type of the request entity (hence a 415(Unsupported Media Type) status code is inappropriate), and the syntax of the request entity is correct (thus a 400 (Bad Request) status code is inappropriate) but was unable to process the contained instructions.',
                'RFC5218#10.3',
                'http://tools.ietf.org/html/rfc2518#section-10.3'
            ],
            423: [
                'Locked',
                'means the source or destination resource of a method is locked.',
                'RFC5218#10.4',
                'http://tools.ietf.org/html/rfc2518#section-10.4'
            ],
            424: [
                'Failed Dependency',
                'means that the method could not be performed on the resource because the requested action depended on another action and that action failed.',
                'RFC5218#10.5',
                'http://tools.ietf.org/html/rfc2518#section-10.5'
            ],
            426: [
                'Upgrade Required',
                'indicates that the server refuses to perform the request using the current protocol but might be willing to do so after the client upgrades to a different protocol.',
                'RFC7231#6.5.15',
                'http://tools.ietf.org/html/rfc7231#section-6.5.15'
            ],
            428: [
                'Precondition Required',
                'indicates that the origin server requires the request to be conditional.',
                'RFC6585#3',
                'http://tools.ietf.org/html/rfc6585#section-3'
            ],
            429: [
                'Too Many Requests',
                'indicates that the user has sent too many requests in a given amount of time (\"rate limiting\").',
                'RFC6585#4',
                'http://tools.ietf.org/html/rfc6585#section-4'
            ],
            431: [
                'Request Header Fields Too Large',
                'indicates that the server is unwilling to process the request because its header fields are too large.',
                'RFC6585#5',
                'http://tools.ietf.org/html/rfc6585#section-5'
            ],
            451: [
                'Unavailable For Legal Reasons',
                'This status code indicates that the server is denying access to the resource in response to a legal demand.',
                'draft-tbray-http-legally-restricted-status',
                'http://tools.ietf.org/html/draft-tbray-http-legally-restricted-status'
            ],
            500: [
                'Internal Server Error',
                'indicates that the server encountered an unexpected condition that prevented it from fulfilling the request.',
                'RFC7231#6.6.1',
                'http://tools.ietf.org/html/rfc7231#section-6.6.1'
            ],
            501: [
                'Not Implemented',
                'indicates that the server does not support the functionality required to fulfill the request.',
                'RFC7231#6.6.2',
                'http://tools.ietf.org/html/rfc7231#section-6.6.2'
            ],
            502: [
                'Bad Gateway',
                'indicates that the server, while acting as a gateway or proxy, received an invalid response from an inbound server it accessed while attempting to fulfill the request.',
                'RFC7231#6.6.3',
                'http://tools.ietf.org/html/rfc7231#section-6.6.3'
            ],
            503: [
                'Service Unavailable',
                'indicates that the server is currently unable to handle the request due to a temporary overload or scheduled maintenance, which will likely be alleviated after some delay.',
                'RFC7231#6.6.4',
                'http://tools.ietf.org/html/rfc7231#section-6.6.4'
            ],
            504: [
                'Gateway Time-out',
                'indicates that the server, while acting as a gateway or proxy, did not receive a timely response from an upstream server it needed to access in order to complete the request.',
                'RFC7231#6.6.5',
                'http://tools.ietf.org/html/rfc7231#section-6.6.5'
            ],
            505: [
                'HTTP Version Not Supported',
                'indicates that the server does not support, or refuses to support, the protocol version that was used in the request message.',
                'RFC7231#6.6.6',
                'http://tools.ietf.org/html/rfc7231#section-6.6.6'
            ],
            506: [
                'Variant Also Negotiates',
                'indicates that the server has an internal configuration error: the chosen variant resource is configured to engage in transparent content negotiation itself, and is therefore not a proper end point in the negotiation process.',
                'RFC2295#8.1',
                'http://tools.ietf.org/html/rfc2295#section-8.1'
            ],
            507: [
                'Insufficient Storage',
                'means the method could not be performed on the resource because the server is unable to store the representation needed to successfully complete the request.',
                'RFC5218#10.6',
                'http://tools.ietf.org/html/rfc2518#section-10.6'
            ],
            511: [
                'Network Authentication Required',
                'indicates that the client needs to authenticate to gain network access.',
                'RFC6585#6',
                'http://tools.ietf.org/html/rfc6585#section-6'
            ],
            '1xx': [
                '**Informational**',
                'indicates an interim response for communicating connection status or request progress prior to completing the requested action and sending a final response. ~ [sure](http://www.urbandictionary.com/define.php?term=sure)',
                'RFC7231#6.2',
                'http://tools.ietf.org/html/rfc7231#section-6.2'
            ],
            '2xx': [
                '**Successful**',
                'indicates that the client\'s request was successfully received, understood, and accepted. ~ [cool](https://twitter.com/DanaDanger/status/183316183494311936)',
                'RFC7231#6.3',
                'http://tools.ietf.org/html/rfc7231#section-6.3'
            ],
            '3xx': [
                '**Redirection**',
                'indicates that further action needs to be taken by the user agent in order to fulfill the request. ~ [ask that dude over there](https://twitter.com/DanaDanger/status/183316183494311936)',
                'RFC7231#6.4',
                'http://tools.ietf.org/html/rfc7231#section-6.4'
            ],
            '4xx': [
                '**Client Error**',
                'indicates that the client seems to have erred. ~ [*you* fucked up](https://twitter.com/DanaDanger/status/183316183494311936)',
                'RFC7231#6.5',
                'http://tools.ietf.org/html/rfc7231#section-6.5'
            ],
            '5xx': [
                '**Server Error**',
                'indicates that the server is aware that it has erred or is incapable of performing the requested method. ~ [*we* fucked up](https://twitter.com/DanaDanger/status/183316183494311936)',
                'RFC7231#6.6',
                'http://tools.ietf.org/html/rfc7231#section-6.6'
            ],
            '7xx': [
                '**Developer Error**',
                '[err](http://www.urbandictionary.com/define.php?term=err)',
                '7xx-rfc',
                'http://documentup.com/joho/7XX-rfc'
            ]
        },
        header: {
            'content-encoding': [
                'Content-Encoding',
                'indicates what content codings have been applied to the representation, beyond those inherent in the media type, and thus what decoding mechanisms have to be applied in order to obtain data in the media type referenced by the Content-Type header field.',
                'RFC7231#3.1.2.2',
                'http://tools.ietf.org/html/rfc7231#section-3.1.2.2'
            ],
            'content-language': [
                'Content-Language',
                'describes the natural language(s) of the intended audience for the representation.',
                'RFC7231#3.1.3.2',
                'http://tools.ietf.org/html/rfc7231#section-3.1.3.2'
            ],
            'content-location': [
                'Content-Location',
                'references a URI that can be used as an identifier for a specific resource corresponding to the representation in this message\'s payload.',
                'RFC7231#3.1.4.2',
                'http://tools.ietf.org/html/rfc7231#section-3.1.4.2'
            ],
            'content-type': [
                'Content-Type',
                'indicates the media type of the associated representation: either the representation enclosed in the message payload or the selected representation, as determined by the message semantics.',
                'RFC7231#3.1.1.5',
                'http://tools.ietf.org/html/rfc7231#section-3.1.1.5'
            ],
            'content-length': [
                'Content-Length',
                'can provide the anticipated size, as a decimal number of octets, for a potential payload body.',
                'RFC7230#3.3.2',
                'http://tools.ietf.org/html/rfc7230#section-3.3.2'
            ],
            'content-range': [
                'Content-Range',
                'is sent in a single part 206 (Partial Content) response to indicate the partial range of the selected representation enclosed as the message payload, sent in each part of a multipart 206 response to indicate the range enclosed within each body part, and sent in 416 (Range Not Satisfiable) responses to provide information about the selected representation.',
                'RFC7233#4.2',
                'http://tools.ietf.org/html/rfc7233#section-4.2'
            ],
            'transfer-encoding': [
                'Transfer-Encoding',
                'lists the transfer coding names corresponding to the sequence of transfer codings that have been (or will be) applied to the payload body in order to form the message body.',
                'RFC7230#3.3.1',
                'http://tools.ietf.org/html/rfc7230#section-3.3.1'
            ],
            'cache-control': [
                'Cache-Control',
                'is used to specify directives for caches along the request/response chain.',
                'RFC7234#7.2',
                'http://tools.ietf.org/html/rfc7234#section-7.2'
            ],
            expect: [
                'Expect',
                'is used to indicate that particular server behaviors are required by the client.',
                'RFC7231#5.1.1',
                'http://tools.ietf.org/html/rfc7231#section-5.1.1'
            ],
            host: [
                'Host',
                'provides the host and port information from the target URI, enabling the origin server to distinguish among resources while servicing requests for multiple host names on a single IP address.',
                'RFC7230#5.4',
                'http://tools.ietf.org/html/rfc7230#section-5.4'
            ],
            'max-forwards': [
                'Max-Forwards',
                'provides a mechanism with the TRACE and OPTIONS methods to limit the number of times that the request is forwarded by proxies.',
                'RFC7231#5.1.2',
                'http://tools.ietf.org/html/rfc7231#section-5.1.2'
            ],
            pragma: [
                'Pragma',
                'allows backwards compatibility with HTTP/1.0 caches, so that clients can specify a \"no-cache\" request that they will understand (as Cache-Control was not defined until HTTP/1.1).',
                'RFC7234#7.4',
                'http://tools.ietf.org/html/rfc7234#section-7.4'
            ],
            range: [
                'Range',
                'modifies the method semantics to request transfer of only one or more subranges of the selected representation data, rather than the entire selected representation data.',
                'RFC7233#3.1',
                'http://tools.ietf.org/html/rfc7233#section-3.1'
            ],
            te: [
                'TE',
                'indicates what transfer codings, besides chunked, the client is willing to accept in response, and whether or not the client is willing to accept trailer fields in a chunked transfer coding.',
                'RFC7230#4.3',
                'http://tools.ietf.org/html/rfc7230#section-4.3'
            ],
            'if-match': [
                'If-Match',
                'can be used to make a request method conditional on the current existence or value of an entity-tag for one or more representations of the target resource.',
                'RFC7232#3.1',
                'http://tools.ietf.org/html/rfc7232#section-3.1'
            ],
            'if-modified-since': [
                'If-Modified-Since',
                'can be used with GET or HEAD to make the method conditional by modification date: if the selected representation has not been modified since the time specified in this field, then do not perform the request method; instead, respond as detailed below.',
                'RFC7232#3.3',
                'http://tools.ietf.org/html/rfc7232#section-3.3'
            ],
            'if-none-match': [
                'If-None-Match',
                'can be used to make a request method conditional on not matching any of the current entity-tag values for representations of the target resource.',
                'RFC7232#3.2',
                'http://tools.ietf.org/html/rfc7232#section-3.2'
            ],
            'if-range': [
                'If-Range',
                'Informally, its meaning is: if the representation is unchanged, send me the part(s) that I am requesting in Range; otherwise, send me the entire representation.',
                'RFC7233#3.2',
                'http://tools.ietf.org/html/rfc7233#section-3.2'
            ],
            'if-unmodified-since': [
                'If-Unmodified-Since',
                'can be used to make a request method conditional by modification date: if the selected representation has been modified since the time specified in this field, then the server MUST NOT perform the requested operation and MUST instead respond with the 412 (Precondition Failed) status code.',
                'RFC7232#3.4',
                'http://tools.ietf.org/html/rfc7232#section-3.4'
            ],
            accept: [
                'Accept',
                'can be used to specify certain media types which are acceptable for the response.',
                'RFC7231#5.3.2',
                'http://tools.ietf.org/html/rfc7231#section-5.3.2'
            ],
            'accept-charset': [
                'Accept-Charset',
                'can be sent by a user agent to indicate what charsets are acceptable in textual response content.',
                'RFC7231#5.3.3',
                'http://tools.ietf.org/html/rfc7231#section-5.3.3'
            ],
            'accept-encoding': [
                'Accept-Encoding',
                'can be used by user agents to indicate what response content-codings are acceptable in the response.',
                'RFC7231#5.3.4',
                'http://tools.ietf.org/html/rfc7231#section-5.3.4'
            ],
            'accept-language': [
                'Accept-Language',
                'can be used by user agents to indicate the set of natural languages that are preferred in the response.',
                'RFC7231#5.3.5',
                'http://tools.ietf.org/html/rfc7231#section-5.3.5'
            ],
            authorization: [
                'Authorization',
                'allows a user agent to authenticate itself with a server -- usually, but not necessarily, after receiving a 401 (Unauthorized) response.',
                'RFC7235#4.1',
                'http://tools.ietf.org/html/rfc7235#section-4.1'
            ],
            'proxy-authorization': [
                'Proxy-Authorization',
                'allows the client to identify itself (or its user) to a proxy that requires authentication.',
                'RFC7235#4.3',
                'http://tools.ietf.org/html/rfc7235#section-4.3'
            ],
            dnt: [
                'DNT',
                'defined as the means for expressing a user\'s tracking preference via HTTP.',
                'Tracking Preference Expression (DNT)',
                'http://www.w3.org/TR/tracking-dnt/#dnt-header-field'
            ],
            from: [
                'From',
                'contains an Internet email address for a human user who controls the requesting user agent.',
                'RFC7231#5.5.1',
                'http://tools.ietf.org/html/rfc7231#section-5.5.1'
            ],
            referer: [
                'Referer',
                'allows the user agent to specify a URI reference for the resource from which the target URI was obtained (i.e., the \"referrer\", though the field name is misspelled).',
                'RFC7231#5.5.2',
                'http://tools.ietf.org/html/rfc7231#section-5.5.2'
            ],
            'user-agent': [
                'User-Agent',
                'contains information about the user agent originating the request, which is often used by servers to help identify the scope of reported interoperability problems, to work around or tailor responses to avoid particular user agent limitations, and for analytics regarding browser or operating system use.',
                'RFC7231#5.5.3',
                'http://tools.ietf.org/html/rfc7231#section-5.5.3'
            ],
            age: [
                'Age',
                'conveys the sender\'s estimate of the amount of time since the response was generated or successfully validated at the origin server.',
                'RFC7234#5.1',
                'http://tools.ietf.org/html/rfc7234#section-5.1'
            ],
            expires: [
                'Expires',
                'gives the date/time after which the response is considered stale.',
                'RFC7234#7.3',
                'http://tools.ietf.org/html/rfc7234#section-7.3'
            ],
            date: [
                'Date',
                'represents the date and time at which the message was originated',
                'RFC7231#7.1.1.2',
                'http://tools.ietf.org/html/rfc7231#section-7.1.1.2'
            ],
            location: [
                'Location',
                'is used in some responses to refer to a specific resource in relation to the response.',
                'RFC7231#7.1.2',
                'http://tools.ietf.org/html/rfc7231#section-7.1.2'
            ],
            'retry-after': [
                'Retry-After',
                'indicates how long the user agent ought to wait before making a follow-up request.',
                'RFC7231#7.1.3',
                'http://tools.ietf.org/html/rfc7231#section-7.1.3'
            ],
            tk: [
                'Tk',
                'defined as an OPTIONAL means for indicating the tracking status that applied to the corresponding request and as a REQUIRED means for indicating that a state-changing request has resulted in an interactive change to the tracking status. ',
                'Tracking Preference Expression (DNT)',
                'http://www.w3.org/TR/tracking-dnt/#response-header-field'
            ],
            vary: [
                'Vary',
                'describes what parts of a request message, aside from the method and request target, might influence the origin server\'s process for selecting and representing the response.',
                'RFC7231#7.1.4',
                'http://tools.ietf.org/html/rfc7231#section-7.1.4'
            ],
            warning: [
                'Warning',
                'is used to carry additional information about the status or transformation of a message that might not be reflected in the message.',
                'RFC7234#7.6',
                'http://tools.ietf.org/html/rfc7234#section-7.6'
            ],
            etag: [
                'ETag',
                'provides the current entity-tag for the selected representation, as determined at the conclusion of handling the request.',
                'RFC7232#2.3',
                'http://tools.ietf.org/html/rfc7232#section-2.3'
            ],
            'last-modified': [
                'Last-Modified',
                'provides a timestamp indicating the date and time at which the origin server believes the selected representation was last modified, as determined at the conclusion of handling the request.',
                'RFC7232#2.2',
                'http://tools.ietf.org/html/rfc7232#section-2.2'
            ],
            'www-authenticate': [
                'WWW-Authenticate',
                'consists of at least one challenge that indicates the authentication scheme(s) and parameters applicable to the effective request URI.',
                'RFC7235#4.4',
                'http://tools.ietf.org/html/rfc7235#section-4.4'
            ],
            'proxy-authenticate': [
                'Proxy-Authenticate',
                'consists of at least one challenge that indicates the authentication scheme(s) and parameters applicable to the proxy for this effective request URI.',
                'RFC7235#4.2',
                'http://tools.ietf.org/html/rfc7235#section-4.2'
            ],
            'accept-ranges': [
                'Accept-Ranges',
                'allows a server to indicate that it supports range requests for the target resource.',
                'RFC7233#2.3',
                'http://tools.ietf.org/html/rfc7233#section-2.3'
            ],
            allow: [
                'Allow',
                'lists the set of methods advertised as supported by the target resource.',
                'RFC7231#7.4.1',
                'http://tools.ietf.org/html/rfc7231#section-7.4.1'
            ],
            server: [
                'Server',
                'contains information about the software used by the origin server to handle the request, which is often used by clients to help identify the scope of reported interoperability problems, to work around or tailor requests to avoid particular server limitations, and for analytics regarding server or operating system use.',
                'RFC7231#7.4.2',
                'http://tools.ietf.org/html/rfc7231#section-7.4.2'
            ],
            'accept-patch': [
                'Accept-Patch',
                'used to specify the patch document formats accepted by the server.',
                'RFC5789#3.1',
                'http://tools.ietf.org/html/rfc5789#section-3.1'
            ],
            'accept-post': [
                'Accept-Post',
                'indicates server support for specific media types for entity bodies in HTTP POST requests.',
                'draft-wilde-accept-post',
                'http://tools.ietf.org/html/draft-wilde-accept-post'
            ],
            'access-control-allow-credentials': [
                'Access-Control-Allow-Credentials',
                'indicates whether the response to request can be exposed when the omit credentials flag is unset',
                'CORS',
                'http://www.w3.org/TR/cors/#access-control-allow-credentials-response-header'
            ],
            'access-control-allow-headers': [
                'Access-Control-Allow-Headers',
                'indicates, as part of the response to a preflight request, which header field names can be used during the actual request',
                'CORS',
                'http://www.w3.org/TR/cors/#access-control-allow-headers-response-header'
            ],
            'access-control-allow-methods': [
                'Access-Control-Allow-Methods',
                'indicates, as part of the response to a preflight request, which methods can be used during the actual request',
                'CORS',
                'http://www.w3.org/TR/cors/#access-control-allow-methods-response-header'
            ],
            'access-control-allow-origin': [
                'Access-Control-Allow-Origin',
                'indicates whether a resource can be shared',
                'CORS',
                'http://www.w3.org/TR/cors/#access-control-allow-origin-response-header'
            ],
            'access-control-expose-headers': [
                'Access-Control-Expose-Headers',
                'indicates which headers are safe to expose to the API of a CORS API specification',
                'CORS',
                'http://www.w3.org/TR/cors/#access-control-expose-headers-response-header'
            ],
            'access-control-max-age': [
                'Access-Control-Max-Age',
                'indicates how long the results of a preflight request can be cached in a preflight result cache',
                'CORS',
                'http://www.w3.org/TR/cors/#access-control-max-age-response-header'
            ],
            'access-control-request-headers': [
                'Access-Control-Request-Headers',
                'indicates which headers will be used in the actual request as part of the preflight request',
                'CORS',
                'http://www.w3.org/TR/cors/#access-control-request-headers-request-header'
            ],
            'access-control-request-method': [
                'Access-Control-Request-Method',
                'indicates which method will be used in the actual request as part of the preflight request',
                'CORS',
                'http://www.w3.org/TR/cors/#access-control-request-method-request-header'
            ],
            'content-disposition': [
                'Content-Disposition',
                'standard',
                'RFC6266',
                'http://tools.ietf.org/html/rfc6266'
            ],
            'content-security-policy': [
                'Content-Security-Policy',
                'is the preferred mechanism for delivering a CSP policy',
                'CSP',
                'http://www.w3.org/TR/CSP/#content-security-policy-header-field'
            ],
            'content-security-policy-report-only': [
                'Content-Security-Policy-Report-Only',
                'lets servers experiment with policies by monitoring (rather than enforcing) a policy',
                'CSP',
                'http://www.w3.org/TR/CSP/#content-security-policy-report-only-header-field'
            ],
            cookie: [
                'Cookie',
                'standard',
                'RFC6265',
                'http://tools.ietf.org/html/rfc6265'
            ],
            forwarded: [
                'Forwarded',
                'standard',
                'RFC7239',
                'http://tools.ietf.org/html/rfc7239'
            ],
            link: [
                'Link',
                'provides a means for serialising one or more links in HTTP headers.',
                'RFC5988#5',
                'http://tools.ietf.org/html/rfc5988#section-5'
            ],
            origin: [
                'Origin',
                'standard',
                'RFC6454',
                'http://tools.ietf.org/html/rfc6454'
            ],
            prefer: [
                'Prefer',
                'is used to indicate that particular server behaviors are preferred by the client, but not required for successful completion of the request.',
                'draft-snell-http-prefer#2',
                'http://tools.ietf.org/html/draft-snell-http-prefer#section-2'
            ],
            'preference-applied': [
                'Preference-Applied',
                'MAY be included within a response message as an indication as to which Prefer tokens were honored by the server and applied to the processing of a request.',
                'draft-snell-http-prefer#3',
                'http://tools.ietf.org/html/draft-snell-http-prefer#section-3'
            ],
            'set-cookie': [
                'Set-Cookie',
                'standard',
                'RFC6265',
                'http://tools.ietf.org/html/rfc6265'
            ],
            'strict-transport-security': [
                'Strict-Transport-Security',
                'standard',
                'RFC6797',
                'http://tools.ietf.org/html/rfc6797'
            ],
            via: [
                'Via',
                '',
                'RFC7230#5.7.1',
                'http://tools.ietf.org/html/rfc7230#section-5.7.1'
            ],
            'a-im': [
                'A-IM',
                '',
                'RFC3229#10.5.3',
                'http://tools.ietf.org/html/rfc3229#section-10.5.3'
            ],
            'accept-features': [
                'Accept-Features',
                'can be used by a user agent to give information about the presence or absence of certain features in the feature set of the current request.',
                'RFC2295#8.2',
                'http://tools.ietf.org/html/rfc2295#section-8.2'
            ],
            'alt-svc': [
                'Alt-Svc',
                'is advertising the availability of alternate services to HTTP/1.1 and HTTP/2.0 clients by adding an Alt-Svc header field to responses.',
                'draft-nottingham-httpbis-alt-svc',
                'http://tools.ietf.org/html/draft-nottingham-httpbis-alt-svc'
            ],
            alternates: [
                'Alternates',
                'is used to convey the list of variants bound to a negotiable resource.',
                'RFC2295#8.3',
                'http://tools.ietf.org/html/rfc2295#section-8.3'
            ],
            'apply-to-redirect-ref': [
                'Apply-To-Redirect-Ref',
                '',
                'RFC4437',
                'http://tools.ietf.org/html/rfc4437'
            ],
            ch: [
                'CH',
                'describes an example list of client preferences that the server can use to adapt and optimize the resource to satisfy a given request.',
                'draft-grigorik-http-client-hints',
                'http://tools.ietf.org/html/draft-grigorik-http-client-hints'
            ],
            'content-base': [
                'Content-Base',
                'obsoleted',
                'RFC2068',
                'http://tools.ietf.org/html/rfc2068'
            ],
            cookie2: [
                'Cookie2',
                'obsoleted',
                'RFC2965',
                'http://tools.ietf.org/html/rfc2965'
            ],
            dasl: [
                'DASL',
                'standard',
                'RFC5323',
                'http://tools.ietf.org/html/rfc5323'
            ],
            dav: [
                'DAV',
                'standard',
                'RFC4918',
                'http://tools.ietf.org/html/rfc4918'
            ],
            'delta-base': [
                'Delta-Base',
                '',
                'RFC3229#10.5.1',
                'http://tools.ietf.org/html/rfc3229#section-10.5.1'
            ],
            depth: [
                'Depth',
                'standard',
                'RFC4918',
                'http://tools.ietf.org/html/rfc4918'
            ],
            destination: [
                'Destination',
                'standard',
                'RFC4918',
                'http://tools.ietf.org/html/rfc4918'
            ],
            im: [
                'IM',
                '',
                'RFC3229#10.5.2',
                'http://tools.ietf.org/html/rfc3229#section-10.5.2'
            ],
            if: [
                'If',
                'standard',
                'RFC4918',
                'http://tools.ietf.org/html/rfc4918'
            ],
            'if-schedule-tag-match': [
                'If-Schedule-Tag-Match',
                'standard',
                'RFC6638',
                'http://tools.ietf.org/html/rfc6638'
            ],
            'last-event-id': [
                'Last-Event-ID',
                'The value of the event source\'s last event ID string, encoded as UTF-8.',
                'Server-Sent Events',
                'http://www.w3.org/TR/eventsource/#last-event-id'
            ],
            'link-template': [
                'Link-Template',
                'provides a means for serialising one or more links into HTTP headers.',
                'draft-nottingham-link-template',
                'http://tools.ietf.org/html/draft-nottingham-link-template'
            ],
            'lock-token': [
                'Lock-Token',
                'standard',
                'RFC4918',
                'http://tools.ietf.org/html/rfc4918'
            ],
            negotiate: [
                'Negotiate',
                'can contain directives for any content negotiation process initiated by the request.',
                'RFC2295#8.4',
                'http://tools.ietf.org/html/rfc2295#section-8.4'
            ],
            nice: [
                'Nice',
                'indicates that a request is less important than a request that doesn\'t bear this header.',
                'draft-thomson-http-nice',
                'http://tools.ietf.org/html/draft-thomson-http-nice'
            ],
            overwrite: [
                'Overwrite',
                'standard',
                'RFC4918',
                'http://tools.ietf.org/html/rfc4918'
            ],
            'redirect-ref': [
                'Redirect-Ref',
                '',
                'RFC4437',
                'http://tools.ietf.org/html/rfc4437'
            ],
            'schedule-reply': [
                'Schedule-Reply',
                'standard',
                'RFC6638',
                'http://tools.ietf.org/html/rfc6638'
            ],
            'schedule-tag': [
                'Schedule-Tag',
                'standard',
                'RFC6638',
                'http://tools.ietf.org/html/rfc6638'
            ],
            'sec-websocket-accept': [
                'Sec-WebSocket-Accept',
                'standard',
                'RFC6455',
                'http://tools.ietf.org/html/rfc6455'
            ],
            'sec-websocket-extensions': [
                'Sec-WebSocket-Extensions',
                'standard',
                'RFC6455',
                'http://tools.ietf.org/html/rfc6455'
            ],
            'sec-websocket-key': [
                'Sec-WebSocket-Key',
                'standard',
                'RFC6455',
                'http://tools.ietf.org/html/rfc6455'
            ],
            'sec-websocket-protocol': [
                'Sec-WebSocket-Protocol',
                'standard',
                'RFC6455',
                'http://tools.ietf.org/html/rfc6455'
            ],
            'sec-websocket-version': [
                'Sec-WebSocket-Version',
                'standard',
                'RFC6455',
                'http://tools.ietf.org/html/rfc6455'
            ],
            'set-cookie2': [
                'Set-Cookie2',
                'obsoleted',
                'RFC2965',
                'http://tools.ietf.org/html/rfc2965'
            ],
            slug: [
                'SLUG',
                'standard',
                'RFC5023',
                'http://tools.ietf.org/html/rfc5023'
            ],
            tcn: [
                'TCN',
                'is used by a server to signal that the resource is transparently negotiated.',
                'RFC2295#8.5',
                'http://tools.ietf.org/html/rfc2295#section-8.5'
            ],
            timeout: [
                'Timeout',
                'standard',
                'RFC4918',
                'http://tools.ietf.org/html/rfc4918'
            ],
            'variant-vary': [
                'Variant-Vary',
                'can be used in a choice response to record any vary information which applies to the variant data (the entity body combined with some of the entity headers) contained in the response, rather than to the response as a whole.',
                'RFC2295#8.6',
                'http://tools.ietf.org/html/rfc2295#section-8.6'
            ],
            'x-frame-options': [
                'X-Frame-Options',
                'indicates a policy that specifies whether the browser should render the transmitted resource within a <frame> or an <iframe>. Servers can declare this policy in the header of their HTTP responses to prevent clickjacking attacks, which ensures that their content is not embedded into other pages or frames.',
                'RFC7034',
                'http://tools.ietf.org/html/rfc7034'
            ]
        }
    });

'use strict';

angular.module('sw.ui.md')
    .factory('display', ["$window", function ($window) {
        return {
            meta: meta
        };

        function meta (i, url, validatorUrl, download) {
            i.contact = i.contact || {};
            i.license = i.license || {};

            var validatorDebug = (validatorUrl && url) ? (validatorUrl + '/debug?url=' + url) : null;
            var validatorBadge = validatorUrl + '?url=' + url;

            return [
                ['Contact', 'person', (i.contact.name && !i.contact.email) ? i.contact.name : null, null],
                ['Email', 'email', i.contact.email ? (i.contact.name || i.contact.email) : null, 'mailto:' + i.contact.email + '?subject=' + i.title],
                ['License', 'vpn_key', i.license.name || i.license.url, i.license.url],
                ['Terms of service', 'assignment', i.termsOfService, i.termsOfService],
                ['Client registration', 'assignment_ind', i['x-apiClientRegistration'] && i['x-apiClientRegistration'].url, i['x-apiClientRegistration'] && i['x-apiClientRegistration'].url],
                ['Documentation', 'help_outline', i.externalDocs && (i.externalDocs.description || i.externalDocs.url), i.externalDocs && i.externalDocs.url],
                ['Host', 'home', i.scheme + '://' + i.host, i.scheme + '://' + i.host],
                ['Base URL', 'link', i.basePath, (i.scheme ? (i.scheme + '://') : '') + i.host + i.basePath],
                ['API version', 'developer_board', i.version, null],
                ['JSON', 'file_download', 'swagger.json', '#', download],
                ['YAML', 'file_download', $window.jsyaml ? 'swagger.yaml' : null, '#', download],
                ['Origin', 'cloud_download', i['x-origin'] && i['x-origin'].url, i['x-origin'] && i['x-origin'].url],
                [null, 'code', validatorDebug, validatorBadge]
            ];
        }
    }]);

'use strict';

angular.module('sw.ui.md')
    .factory('dialog', ["$mdDialog", function ($mdDialog) {
        DialogCtrl.$inject = ["$scope", "$mdDialog", "vm"];
        return {
            show: show
        };

        function show ($event, locals, type) {
            return $mdDialog.show({
                templateUrl: 'views/' + (type || 'info') + '.dialog.html',
                clickOutsideToClose: true,
                targetEvent: $event,
                controller: DialogCtrl,
                locals: {vm: locals}
            });
        }

        function DialogCtrl ($scope, $mdDialog, vm) {
            $scope.vm = vm;
            $scope.vm.opened = true;
            $scope.closeDialog = function () {
                $scope.vm.opened = false;
                $mdDialog.hide();
            };
        }
    }]);

/*
 * Orange angular-swagger-ui - v0.3.0
 *
 * (C) 2015 Orange, all right reserved
 * MIT Licensed
 */
'use strict';

angular.module('sw.ui', [
    'sw.plugins'
]);

/*
 * Orange angular-swagger-ui - v0.3.0
 *
 * (C) 2015 Orange, all right reserved
 * MIT Licensed
 */
'use strict';

angular
    .module('sw.ui')
    .factory('model', ["$log", function ($log) {
        /**
         * sample object cache to avoid generating the same one multiple times
         */
        var objCache = {};

        /**
         * model cache to avoid generating the same one multiple times
         */
        var modelCache = {};

        /**
         * inline model counter
         */
        var countInLine = 0;

        return {
            generateModel: generateModel,
            getType: getType,
            resolveReference: resolveReference,
            generateSampleJson: generateSampleJson,
            getSampleObj: getSampleObj,
            clearCache: clearCache
        };

        /**
         * clears generated models cache
         */
        function clearCache () {
            objCache = {};
            modelCache = {};
        }

        /**
         * retrieves object definition
         */
        function resolveReference (swagger, object) {
            if (object.$ref) {
                var parts = object.$ref.replace('#/', '').split('/');
                object = swagger;
                for (var i = 0, j = parts.length; i < j; i++) {
                    object = object[parts[i]];
                }
            }
            return object;
        }

        /**
         * determines a property type
         */
        function getType (item) {
            var format = item.format;
            switch (format) {
                case 'int32':
                    format = item.type;
                    break;
                case 'int64':
                    format = 'long';
                    break;
            }
            return format || item.type;
        }

        /**
         * retrieves object class name based on $ref
         */
        function getClassName (item) {
            var parts = item.$ref.split('/');
            return parts[parts.length - 1];
        }

        /**
         * generates a sample object (request body or response body)
         */
        function getSampleObj (swagger, schema, currentGenerated) {
            var sample;
            currentGenerated = currentGenerated || {}; // used to handle circular references
            if (schema.default || schema.example) {
                sample = schema.default || schema.example;
            } else if (schema.properties) {
                sample = {};

                angular.forEach(schema.properties, function (v, name) {
                    sample[name] = getSampleObj(swagger, v, currentGenerated);
                });
            } else if (schema.$ref) {
                // complex object
                var def = resolveReference(swagger, schema);

                if (def) {
                    if (!objCache[schema.$ref] && !currentGenerated[schema.$ref]) {
                        // object not in cache
                        currentGenerated[schema.$ref] = true;
                        objCache[schema.$ref] = getSampleObj(swagger, def, currentGenerated);
                    }

                    sample = objCache[schema.$ref] || {};
                } else {
                    $log.warn('schema not found', schema.$ref);
                }
            } else if (schema.type === 'array') {
                sample = [getSampleObj(swagger, schema.items, currentGenerated)];
            } else if (schema.type === 'object') {
                sample = {};
            } else {
                sample = schema.defaultValue || schema.example || getSampleValue(getType(schema));
            }
            return sample;
        }

        /**
         * generates a sample value for a basic type
         */
        function getSampleValue (type) {
            var result;
            switch (type) {
                case 'long':
                case 'integer':
                    result = 0;
                    break;
                case 'boolean':
                    result = false;
                    break;
                case 'double':
                case 'number':
                    result = 0.0;
                    break;
                case 'string':
                    result = 'string';
                    break;
                case 'date':
                    result = (new Date()).toISOString().split('T')[0];
                    break;
                case 'date-time':
                    result = (new Date()).toISOString();
                    break;
            }
            return result;
        }

        /**
         * generates a sample JSON string (request body or response body)
         */
        function generateSampleJson (swagger, schema) {
            var json;
            var obj = getSampleObj(swagger, schema);

            if (obj) {
                json = angular.toJson(obj, true);
            }

            return json;
        }

        /**
         * generates object's model
         */
        function generateModel (swagger, schema, modelName, currentGenerated) {
            var model = '';
            var buffer;
            var subModels;
            var hasProperties = false;
            var name;
            var className;
            var def;
            var sub;

            currentGenerated = currentGenerated || {}; // used to handle circular references

            function isRequired (item, name) {
                return item.required && item.required.indexOf(name) !== -1;
            }

            if (schema.properties) {
                modelName = modelName || ('Inline Model' + countInLine++);
                currentGenerated[modelName] = true;
                buffer = ['<div><strong>' + modelName + ' {</strong>'];
                subModels = [];

                angular.forEach(schema.properties, function (property, propertyName) {
                    hasProperties = true;
                    buffer.push('<div class="pad"><strong>', propertyName, '</strong> (<span class="type">');

                    // build type
                    if (property.properties) {
                        name = 'Inline Model' + countInLine++;
                        buffer.push(name);
                        subModels.push(generateModel(swagger, property, name, currentGenerated));
                    } else if (property.$ref) {
                        buffer.push(getClassName(property));
                        subModels.push(generateModel(swagger, property, null, currentGenerated));
                    } else if (property.type === 'array') {
                        buffer.push('Array[');
                        if (property.items.properties) {
                            name = 'Inline Model' + countInLine++;
                            buffer.push(name);
                            subModels.push(generateModel(swagger, property, name, currentGenerated));
                        } else if (property.items.$ref) {
                            buffer.push(getClassName(property.items));
                            subModels.push(generateModel(swagger, property.items, null, currentGenerated));
                        } else {
                            buffer.push(getType(property.items));
                        }
                        buffer.push(']');
                    } else {
                        buffer.push(getType(property));
                    }

                    buffer.push('</span>');

                    // is required ?
                    if (!isRequired(schema, propertyName)) {
                        buffer.push(', ', '<em>optional</em>');
                    }

                    buffer.push(')');

                    // has description
                    if (property.description) {
                        buffer.push(': ', property.description);
                    }

                    // is enum
                    if (property.enum) {
                        buffer.push(' = ', angular.toJson(property.enum).replace(/,/g, ' or '));
                    }

                    buffer.push(',</div>');
                });

                if (hasProperties) {
                    buffer.pop();
                    buffer.push('</div>');
                }

                buffer.push('<div><strong>}</strong></div>');
                buffer.push(subModels.join(''), '</div>');
                model = buffer.join('');
            } else if (schema.$ref) {
                className = getClassName(schema);
                def = resolveReference(swagger, schema);

                if (currentGenerated[className]) {
                    return ''; // already generated
                }

                if (def) {
                    if (!modelCache[schema.$ref]) {
                        // cache generated object
                        modelCache[schema.$ref] = generateModel(swagger, def, className, currentGenerated);
                    }
                    currentGenerated[className] = true;
                    model = modelCache[schema.$ref];
                }
            } else if (schema.type === 'array') {
                buffer = ['<strong>Array ['];
                sub = '';

                if (schema.items.properties) {
                    name = 'Inline Model' + countInLine++;
                    buffer.push(name);
                    sub = generateModel(swagger, schema.items, name, currentGenerated);
                } else if (schema.items.$ref) {
                    buffer.push(getClassName(schema.items));
                    sub = generateModel(swagger, schema.items, null, currentGenerated);
                } else {
                    buffer.push(getType(schema.items));
                }

                buffer.push(']</strong><br><br>', sub);
                model = buffer.join('');
            } else if (schema.type === 'object') {
                model = '<strong>Inline Model {<br>}</strong>';
            }

            return model;
        }
    }]);

/*
 * Orange angular-swagger-ui - v0.3.0
 *
 * (C) 2015 Orange, all right reserved
 * MIT Licensed
 */
'use strict';

angular.module('sw.ui')
    .factory('format', function () {
        return {
            fullUrl: fullUrl
        };

        function fullUrl (response) {
            var query = '';
            var config = response.config || {};

            if (config.params) {
                var parts = [];

                angular.forEach(config.params, function (v, k) {
                    parts.push(k + '=' + encodeURIComponent(v));
                });

                if (parts.length > 0) {
                    query = '?' + parts.join('&');
                }
            }

            return config.url + query;
        }
    });

'use strict';

angular.module('sw.ui')
    .factory('data', ["$log", "$rootScope", "$http", "plugins", function ($log, $rootScope, $http, plugins) {
        var self = {
            options: {
                url: null,
                validatorUrl: null,
                parser: 'auto',
                trustedSources: false,
                proxy: null,
                errorHandler: null
            },
            ui: {
                grouped: true,
                descriptions: false,
                explorer: true,
                sidenavOpen: false,
                sidenavLocked: false
            },
            model: {
                info: null,
                groups: null,
                operations: null,
                form: null,
                hasSecurity: false,
                securityDefinitions: null,
                search: {},
                sop: null
            },
            swagger: null,
            loading: false,
            setUrl: setUrl
        };

        function reset () {
            self.swagger = null;

            self.model = {
                info: null,
                groups: null,
                form: null,
                security: null,
                securityDefinitions: null
            };

            $log.debug('sw:reset');
            $rootScope.$broadcast('sw:changed');
        }

        function setUrl (url) {
            if (self.options.url === url) {
                return;
            }

            $log.debug('sw:url', url);

            reset();

            self.options.url = url;

            if (!url) {
                return;
            }

            self.loading = true;

            load(url, function (response) {
                if (response.config.url !== self.options.url) {
                    return;
                }

                self.swagger = response.data;
                plugins
                    .execute(plugins.BEFORE_PARSE, url, self.swagger)
                    .then(function () {
                        var type = (response.headers()['content-type'] || 'application/json').split(';')[0];
                        loaded(url, type);
                        self.loading = false;
                    })
                    .catch(onError);
            }, onError);
        }

        function load (url, callback, onError) {
            var options = {
                method: 'GET',
                url: url
            };

            plugins
                .execute(plugins.BEFORE_LOAD, options)
                .then(function () {
                    $http(options).then(callback, onError);
                })
                .catch(onError);
        }

        function loaded (url, type) {
            var parseResult = {};
            var swaggerCopy = angular.copy(self.swagger);

            $log.debug('sw:loaded');

            plugins
                .execute(
                    plugins.PARSE,
                    self.options.parser,
                    url,
                    type,
                    swaggerCopy,
                    self.options.trustedSources,
                    parseResult)
                .then(function (executed) {
                    if (executed) {
                        parsed(parseResult);
                    } else {
                        onError({
                            message: 'no parser found'
                        });
                    }
                })
                .catch(onError);
        }

        function parsed (parseResult) {
            plugins
                .execute(plugins.BEFORE_DISPLAY, parseResult)
                .then(function () {
                    self.model.info = parseResult.info;
                    self.model.form = parseResult.form;
                    self.model.groups = parseResult.resources;
                    self.model.operations = parseResult.info.operations;
                    self.model.securityDefinitions = parseResult.securityDefinitions;
                    self.model.hasSecurity = hasSecurity(self.swagger);

                    $log.debug('sw:parsed');
                    $rootScope.$broadcast('sw:changed');
                })
                .catch(onError);
        }

        function hasSecurity (swagger) {
            return Object.keys(swagger.securityDefinitions || {}).length;
        }

        function onError (error) {
            self.loading = false;

            if (angular.isFunction(self.options.errorHandler)) {
                self.options.errorHandler(error);
            }
        }

        return self;
    }])
;

/*
 * Orange angular-swagger-ui - v0.3.0
 *
 * (C) 2015 Orange, all right reserved
 * MIT Licensed
 */
'use strict';

angular
    .module('sw.ui')
    .factory('client', ["$q", "$window", "$http", "plugins", function ($q, $window, $http, plugins) {
        return {
            configure: configure,
            send: send,
            base: base
        };

        /**
         * Send API explorer request
         */
        function send (swagger, operation, values, mock) {
            var deferred = $q.defer();
            var baseUrl = base(swagger);
            var options = configure(operation, values, baseUrl);

            function done (response) {
                // execute modules
                plugins
                    .execute(plugins.AFTER_EXPLORER_LOAD, response)
                    .then(function () {
                        deferred.resolve(response);
                    });
            }

            // execute modules
            plugins
                .execute(plugins.BEFORE_EXPLORER_LOAD, options)
                .then(function () {
                    if (mock) {
                        deferred.resolve(options);
                    } else {
                        checkMixedContent(options).then(function () {
                            // send request
                            $http(options).then(done, done);
                        }, done);
                    }
                });

            return deferred.promise;
        }

        function configure (operation, values, baseUrl) {
            var path = operation.path;
            var query = {};
            var headers = {};
            var body = null;

            // build request parameters
            angular.forEach(operation.parameters, function (param) {
                // TODO manage 'collectionFormat' (csv etc.) !!
                var value = values[param.name];

                switch (param.in) {
                    case 'query':
                        if (value) {
                            query[param.name] = value;
                        }
                        break;
                    case 'path':
                        path = path.replace('{' + param.name + '}', encodeURIComponent(value));
                        break;
                    case 'header':
                        if (value) {
                            headers[param.name] = value;
                        }
                        break;
                    case 'formData':
                        body = body || new $window.FormData();
                        if (value) {
                            // make browser defining it by himself
                            values.contentType = (param.type === 'file') ? undefined : values.contentType;
                            body.append(param.name, value);
                        }
                        break;
                    case 'body':
                        body = body || value;
                        break;
                }
            });

            // add headers
            headers.accept = values.responseType;
            headers['content-type'] = body ? values.contentType : 'text/plain';

            return {
                method: operation.httpMethod,
                url: baseUrl + path,
                headers: headers,
                data: body,
                params: query
            };
        }

        function base (swaggerInfo) {
            return [
                swaggerInfo.scheme,
                '://',
                swaggerInfo.host,
                (swaggerInfo.basePath === '/' ? '' : swaggerInfo.basePath) || ''
            ].join('');
        }

        function protocol (url) {
            return angular.element('<a href="' + url + '"></a>')[0].protocol.replace(':');
        }

        function checkMixedContent (options) {
            var deferred = $q.defer();

            if ((protocol($window.location.href) === 'https') && (protocol(options.url) === 'http')) {
                deferred.reject({config: options, status: -1, statusText: 'HTTPS mixed with HTTP content'});
            } else {
                deferred.resolve();
            }

            return deferred.promise;
        }
    }]);

'use strict';

angular.module('sw.ui.directives', []);

'use strict';

angular.module('sw.ui.directives')
    .directive('truncate', ["truncation", function (truncation) {
        return {
            restrict: 'A',
            scope: {
                ngBindHtml: '=',
                ngBind: '='
            },
            link: function (scope, element, attr) {
                scope.$watch('ngBind', update);
                scope.$watch('ngBindHtml', update);

                function update () {
                    var more = angular.element('<a class="truncate">\u2026</a>');

                    element.empty();

                    element.append(truncation(
                        (scope.ngBind ? angular.element('<div></div>').text(scope.ngBind).html() : null) || scope.ngBindHtml,
                        {
                            length: attr.truncate || 144,
                            words: true,
                            ellipsis: more[0]
                        }
                    ));

                    more.bind('click', function (event) {
                        event.preventDefault();
                        event.stopPropagation();
                        if (scope.ngBind) {
                            element[0].textContent = scope.ngBind;
                        } else if (scope.ngBindHtml) {
                            element[0].innerHTML = scope.ngBindHtml;
                        }
                    });
                }
            }
        };
    }])
    .factory('truncation', function () {
        var chop = /(\s*\S+|\s)$/;

        // based on https://github.com/pathable/truncate
        function truncate (root, opts) {
            var text = root.textContent;
            var excess = text.length - opts.length;

            if (opts.words && excess > 0) {
                excess = text.length - text.slice(0, opts.length).replace(chop, '').length - 1;
            }

            if (excess < 0 || !excess && !opts.truncated) return;

            for (var i = root.childNodes.length - 1; i >= 0; i--) {
                var el = root.childNodes[i];
                text = el.textContent;
                var length = text.length;

                if (length <= excess) {
                    opts.truncated = true;
                    excess -= length;
                    el.remove();
                    continue;
                }

                if (el.nodeType === 3) {
                    var s = el.splitText(length - excess - 1);
                    s.parentNode.replaceChild(opts.ellipsis, s);
                    return;
                }

                truncate(el, angular.extend(opts, {length: length - excess}));
                return;
            }
        }

        return function (html, options) {
            var root = angular.element('<div></div>').append(html)[0];
            truncate(root, options);
            return root;
        };
    });

'use strict';

angular.module('sw.ui.directives')
    .directive('toolbarSearch', ["$timeout", function ($timeout) {
        return {
            restrict: 'E',
            templateUrl: 'directives/toolbar-search/toolbar-search.html',
            scope: {
                ngModel: '=',
                ngChanged: '=',
                open: '='
            },
            link: function (scope, element) {
                $timeout(function () {
                    scope.init = true;
                }, 200);

                scope.focus = function () {
                    $timeout(function () {
                        element.children()[1].focus();
                    }, 200);
                };

                scope.$watch('ngModel', scope.ngChanged);
            }
        };
    }]);

'use strict';

angular.module('sw.ui.directives')
    .directive('toolbarEdit', ["$timeout", function ($timeout) {
        return {
            restrict: 'E',
            templateUrl: 'directives/toolbar-edit/toolbar-edit.html',
            scope: {
                ngModel: '=',
                ngChanged: '=',
                displayTitle: '='
            },
            link: function (scope, element) {
                var t;
                scope.open = false;
                scope.init = false;
                $timeout(function () {
                    scope.init = true;
                }, 200);
                scope.focus = function () {
                    $timeout.cancel(t);

                    $timeout(function () {
                        element.children().eq(1).children()[0].focus();
                    }, 200);
                };
                scope.blur = function () {
                    t = $timeout(function () {
                        scope.open = false;
                        scope.ngChanged();
                    }, 200);
                };
                scope.toggle = function () {
                    scope.open = !scope.open;

                    if (scope.open) {
                        scope.focus();
                    } else {
                        scope.ngChanged();
                    }
                };
            }
        };
    }]);

/*
 * Orange angular-swagger-ui - v0.3.0
 *
 * (C) 2015 Orange, all right reserved
 * MIT Licensed
 */
'use strict';

angular
    .module('sw.ui.directives')
    .directive('fileInput', function () {
        // helper to be able to retrieve HTML5 File in ngModel from input
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function (scope, element, attr, ngModel) {
                element.bind('change', function () {
                    scope.$apply(function () {
                        // TODO manage multiple files ?
                        ngModel.$setViewValue(element[0].files[0]);
                    });
                });
            }
        };
    });
