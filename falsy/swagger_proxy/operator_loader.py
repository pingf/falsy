import ast
import base64

import falcon
import json

from falsy.jlog.jlog import JLog


def json_check(value):
    try:
        if type(value) == str:
            try:
                value = json.loads(value)
            except json.decoder.JSONDecodeError as e:
                value = ast.literal_eval(value)
        return value
    except Exception as e:
        raise falcon.HTTPInvalidParam('json check error:', str(e)+' '+str(type(e)))



class OperatorLoader:
    def __init__(self):
        self.log = JLog().bind()

    def load_base(self, spec):
        bid = spec.get('beforeId')
        aid = spec.get('afterId')
        eid = spec.get('exceptionId')
        fid = spec.get('finalId')
        return bid, aid, eid, fid

    def load(self, req, spec, matched_uri):
        vid = spec.get('validationId')
        aid = spec.get('afterId')
        oid = spec.get('operationId')
        bid = spec.get('beforeId')
        eid = spec.get('exceptionId')
        fid = spec.get('finalId')
        omode = spec.get('operationMode')
        return oid, self.load_params(req, spec.get('parameters'), matched_uri, spec, vid), bid, aid, eid, fid, omode

    def load_params(self, req, params, matched_uri, spec, validator):
        if params:
            results = {}
            for param in params:
                name = param.get('name')
                in_ = param.get('in')
                default = param.get('default')
                required = param.get('required')
                # value = None
                if in_ == 'query':
                    value = self.param_in_query(req, param)
                elif in_ == 'path':
                    value = self.param_in_path(matched_uri, param)
                elif in_ == 'body':
                    value = self.param_in_body(req, spec, param)
                elif in_ == 'header':
                    value = self.param_in_header(req, spec, param)
                else:
                    value = None

                if default and value is None:
                    value = default
                vid = param.get('validationId')
                self.custom_validate(vid, value)
                if required or value is not None:
                    results[name] = value
            if len(results) == 0:
                self.custom_validate_all(validator)
            else:
                self.custom_validate_all(validator, **results)
            return results
        self.custom_validate_all(validator)
        return {}

    def custom_validate(self, vid, value):
        validator = vid  # get_function_from_name(vid)
        validated = None
        try:
            if validator:
                validated = validator(value)
        except Exception as e:
            self.log.error_trace('custom validtion failed,vid: {}, value: {}'.format(vid, value))
            raise falcon.HTTPInvalidParam('validation failed, value:', str(value))

        if type(validated) == list or type(validated) == tuple:
            va = validated[0]
            ext = validated[1]
            if va is None or va is False:
                raise falcon.HTTPInvalidParam('invalid param(custom validation), value:', str(value) + ' info:' + ext)
        else:
            if validated is False:
                raise falcon.HTTPInvalidParam('invalid param(custom validation), value:', str(value))

    def custom_validate_all(self, vid, **kwargs):
        validator = vid  # get_function_from_name(vid)
        validated = None
        try:
            if validator:
                validated = validator(**kwargs) if len(kwargs) > 0 else validator(**kwargs)
        except Exception as e:
            raise falcon.HTTPInvalidParam('validation failed, values:', str(kwargs))

        if type(validated) == list or type(validated) == tuple:
            va = validated[0]
            ext = validated[1]
            if va is None or va is False:
                raise falcon.HTTPInvalidParam('invalid param(custom validation all), values:',
                                              str(kwargs) + ' info:' + ext)
        else:
            if validated is False:
                raise falcon.HTTPInvalidParam('invalid param(custom validation all), values:', str(kwargs))

    def param_in_query(self, req, param):
        name = param.get('name')
        type_ = param.get('type')

        default_func = lambda p: req.get_param(p) if type_ is not None else None

        check_funcs = {
            'string': lambda p: req.get_param(p),
            'password': lambda p: req.get_param(p),
            'byte': lambda p: base64.b64decode(req.get_param(p)),
            'integer': lambda p: req.get_param_as_int(p),
            'long': lambda p: req.get_param_as_int(p),
            'float': lambda p: float(req.get_param(p)),
            'double': lambda p: float(req.get_param(p)),
            'array': lambda p: req.get_param_as_dict(p),
            'object': lambda p: req.get_param_as_dict(p),
            'boolean': lambda p: req.get_param_as_bool(p),
        }
        value = None
        try:
            value = check_funcs.get(type_, default_func)(name)
            self.log.debug('param in query - name: {}, type: {}, value: {}'.format(name, type_, value))
        except ValueError as e:
            self.log.error_trace(
                'value error when check param in query - name: {}, type: {}, value: {}'.format(name, type_, value))
            raise falcon.HTTPInvalidParam('invalid param in query', name)
        if param.get('required') and value is None:
            raise falcon.HTTPMissingParam(name)
        return value

    def param_in_path(self, matched_uri, param):
        type_ = param.get('type')
        name = param.get('name')

        value = matched_uri.groupdict().get(name)
        self.log.debug(value)
        default_func = lambda v: v if type_ is not None else None
        check_funcs = {
            'string': lambda v: str(v),
            'password': lambda v: str(v),
            'byte': lambda v: base64.b64decode(str(v)),
            'integer': lambda v: int(v),
            'long': lambda v: int(v),
            'float': lambda v: float(v),
            'double': lambda v: float(v),
            'boolean': lambda v: bool(v),
        }
        if param.get('required') and value is None:
            raise falcon.HTTPMissingParam(name)
        try:
            value = check_funcs.get(type_, default_func)(value)
            self.log.debug('param in path - name: {}, type: {}, value: {}'.format(name, type_, value))
        except ValueError as e:
            self.log.error_trace(
                'value error when check param in path - name: {}, type: {}, value: {}'.format(name, type_, value))
            raise falcon.HTTPInvalidParam('invalid param in path', name)
        return value

    def param_in_header(self, req, spec, param):
        headers = req.headers
        name = param.get('name').upper().replace('_', '-')
        type_ = param.get('type')

        value = headers.get(name)
        if param.get('required') and value is None:
            raise falcon.HTTPMissingParam(name)

        default_func = lambda v: v if type_ is not None else None

        check_funcs = {
            'string': lambda v: str(v),
            'password': lambda v: str(v),
            'byte': lambda v: base64.b64decode(str(v)),
            'integer': lambda v: int(v),
            'long': lambda v: int(v),
            'float': lambda v: float(v),
            'double': lambda v: float(v),
            'boolean': lambda v: bool(v),
            'array': json_check,
            'object': json_check,
        }

        try:
            value = check_funcs.get(type_, default_func)(value)
            self.log.debug('param in header - name: {}, type: {}, value: {}'.format(name, type_, value))
        except ValueError as e:
            self.log.error_trace(
                'value error when check param in header - name: {}, type: {}, value: {}'.format(name, type_, value))
            raise falcon.HTTPInvalidParam('invalid param in header', name + ':' + value)
        if param.get('required') and value is None:
            raise falcon.HTTPMissingParam(name)
        return value

    def param_in_body(self, req, spec, param):
        body = req.stream.read().decode('utf-8')
        schema = spec.get('schema')
        name = param.get('name')
        type_ = schema.get('type')
        value = body

        if param.get('required') and body is None:
            raise falcon.HTTPMissingParam(name)
        default_func = lambda v: v

        check_funcs = {
            'string': lambda v: str(v),
            'password': lambda v: str(v),
            'byte': lambda v: base64.b64decode(str(v)),
            'integer': lambda v: int(v),
            'long': lambda v: int(v),
            'float': lambda v: float(v),
            'double': lambda v: float(v),
            'boolean': lambda v: bool(v),
            'array': json_check,
            'object': json_check,
        }
        try:

            if 'allOf' in schema:
                value = check_funcs.get(type_, json_check)(value)
            else:
                value = check_funcs.get(type_, default_func)(value)
            self.log.debug('param in body - name: {}, type: {}, value: {}'.format(name, type_, value))
        except ValueError as e:
            self.log.error_trace(
                'value error when check param in body - name: {}, type: {}, value: {}'.format(name, type_, value))
            raise falcon.HTTPInvalidParam('invalid param in body', name)
        return value
