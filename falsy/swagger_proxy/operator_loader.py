
import falcon
import json
import logging

from falsy.dynamic_import import get_function_from_name

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class OperatorLoader:
    def load_base(self, spec):
        bid = spec.get('beforeId')
        aid = spec.get('afterId')
        try:
            before = get_function_from_name(bid)
            after = get_function_from_name(aid)
        except Exception as e:
            print(e, type(e))
            print('handler dynamic load error')
            raise falcon.HTTPMissingParam('bid or aid invalid')
        else:
            return before, after

    def load(self, req, spec, matched_uri):
        aid = spec.get('afterId')
        oid = spec.get('operationId')
        bid = spec.get('beforeId')
        omode = spec.get('operationMode')
        try:
            before = get_function_from_name(bid)
            handler = get_function_from_name(oid)
            after = get_function_from_name(aid)
        except Exception as e:
            print(e, type(e))
            print('handler dynamic load error')
            raise falcon.HTTPMissingParam('opid invalid')
        else:
            return handler, self.load_params(req, spec.get('parameters'), matched_uri, spec), before, after, omode

    def load_params(self, req, params, matched_uri, spec):
        if params:
            results = {}
            for param in params:
                name = param.get('name')
                in_ = param.get('in')
                # value = None
                if in_ == 'query':
                    value = self.param_in_query(req, param)
                elif in_ == 'path':
                    value = self.param_in_path(matched_uri, param)
                elif in_ == 'body':
                    value = self.param_in_body(req, spec, param)
                    if type(value) == tuple or type(value) == list:
                        if type(value[0]) == dict and type(value[1]) == str:
                            return value[0]
                else:
                    value = None
                results[name] = value
            return results
        return {}

    def param_in_query(self, req, param):
        name = param.get('name')
        type_ = param.get('type')

        default_func = lambda p: req.get_param(p) if type_ is not None else None

        check_funcs = {
            'string': lambda p: req.get_param(p),
            'integer': lambda p: req.get_param_as_int(p),
            'float': lambda p: float(req.get_param(p)),
            'array': lambda p: req.get_param_as_list(p),
        }
        try:
            value = check_funcs.get(type_, default_func)(name)
        except ValueError as e:
            raise falcon.HTTPInvalidParam('invalid param in query', name)
        if param.get('required') and value is None:
            raise falcon.HTTPMissingParam(name)

        vid = param.get('validationId')
        print(vid, value, param)
        self.custom_validate(vid, value)
        return value

    def custom_validate(self, vid, value):
        if vid:
            try:
                validator = get_function_from_name(vid)
            except Exception as e:
                print(e, type(e))
                print('validator dynamic load error')
                raise falcon.HTTPInvalidParam('invalid param in query(custom validation exception), value:', str(value))
            try:
                if validator:
                    validated = validator(value)
            except Exception as e:
                raise falcon.HTTPInvalidParam('invalid param in query(custom validation exception), value:', str(value))

            if type(validated) == list or type(validated) == tuple:
                va = validated[0]
                ext = validated[1]
                if va is None or va is False:
                    raise falcon.HTTPInvalidParam('invalid param in query(custom validation), value:',
                                                  str(value) + ' info:' + ext)
            else:
                if validated is None or validated is False:
                    raise falcon.HTTPInvalidParam('invalid param in query(custom validation), value:', str(value))

    def param_in_path(self, matched_uri, param):
        type_ = param.get('type')
        name = param.get('name')
        value = matched_uri.groupdict().get(name)
        default_func = lambda v: v if type_ is not None else None
        check_funcs = {
            'string': lambda v: str(v),
            'integer': lambda v: int(v),
            'float': lambda v: float(v),
        }
        if param.get('required') and value is None:
            raise falcon.HTTPMissingParam(name)
        try:
            value = check_funcs.get(type_, default_func)(value)
        except ValueError as e:
            raise falcon.HTTPInvalidParam('invalid param in path', name)
        vid = param.get('validationId')
        self.custom_validate(vid, value)
        return value

    def param_in_body(self, req, spec, param):
        body = req.stream.read().decode('utf-8')
        schema = spec.get('schema')
        name = param.get('name')
        type_ = schema.get('type')
        value = body

        if param.get('required') and body is None:
            raise falcon.HTTPMissingParam(name)
        default_func = lambda v: v if type_ is not None else None

        def array_check(value):
            doc = json.loads(value)
            return doc

        def object_check(value):
            doc = json.loads(value)
            if schema.get('splitted'):
                values = self.param_in_body_splitted(schema, doc)
                return values, 'splitted'
            else:
                return doc

        check_funcs = {
            'string': lambda v: str(v),
            'integer': lambda v: int(v),
            'float': lambda v: float(v),
            'array': array_check,
            'object': object_check,
        }
        try:
            value = check_funcs.get(type_, default_func)(value)
        except ValueError as e:
            raise falcon.HTTPInvalidParam('invalid param in path', name)
        vid = param.get('validationId')
        self.custom_validate(vid, value)
        return value

    def param_in_body_splitted(self, schema, doc):
        values = {}
        properties = schema.get('properties')
        for name, property_ in properties.items():
            required = property_.get('required')
            type_ = property_['type']
            value = doc.get(name)
            if required and value is None:
                raise falcon.HTTPMissingParam(name)

            default_func = lambda v: v if type_ is not None else None
            check_funcs = {
                'string': lambda v: str(v) if value is not None else None,
                'integer': lambda v: int(v) if value is not None else None,
                'float': lambda v: float(v) if value is not None else None,
                'array': lambda v: list(v) if value is not None else None,
            }
            try:
                value = check_funcs.get(type_, default_func)(value)
                vid = property_.get('validationId')
                self.custom_validate(vid, value)
                values[name] = value
            except ValueError as e:
                raise falcon.HTTPInvalidParam('invalid param in path', name)
        return values
