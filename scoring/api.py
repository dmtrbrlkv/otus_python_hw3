#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import namedtuple
import re
from scoring import get_interests, get_score

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
MAX_YEARS_FOR_BIRTHDAY = 70
validation_res = namedtuple("validation_res", ["is_valid", "reason"])


# ====Fields====

class Field(metaclass=ABCMeta):
    """
    Abstract class for fields
    All field classes must inherit from this class
    """

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable
        self.not_valid_add_info = ""

    def __set__(self, instance, value):
        setattr(instance, self.name, value)

    def __get__(self, instance, owner):
        return getattr(instance, self.name, None)

    def __set_name__(self, owner, name):
        self.name = "_" + name
        self.label = name

    @abstractmethod
    def is_not_empty_value(self, instance):
        """
        Return True if value not empty
        Must present in child
        """

    @abstractmethod
    def is_valid_value(self, instance):
        """
        Return True if value is valid
        Must present in child
        """

    def validate(self, instance):
        if self.required and getattr(instance, self.name, None) is None:
            return validation_res(False, f"field '{self.label}' is required")
        if not self.required and getattr(instance, self.name, None) is None:
            return validation_res(True, "")
        if not self.nullable and not self.is_not_empty_value(instance):
            return validation_res(False, f"field '{self.label}' is empty")
        if not self.is_valid_value(instance):
            return validation_res(False, f"field '{self.label}', invalid value: {str(getattr(instance, self.name, None))} "
                                         f"({self.not_valid_add_info})")
        return validation_res(True, "")


class CharField(Field):
    def is_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, str):
            self.not_valid_add_info = "not 'str' type"
            return False
        return True

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, str) and value != ""


class ArgumentsField(Field):
    def is_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, dict):
            self.not_valid_add_info = "not 'dict' type"
            return False
        return True

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, dict) and value


class EmailField(CharField):
    def is_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not super().is_valid_value(instance):
            return False
        if "@" not in value:
            self.not_valid_add_info = "'@' not present"
            return False
        return True

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, str) and value != ""


class PhoneField(Field):
    def is_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, (int, str)):
            self.not_valid_add_info = "not '(int, str)' type"
            return False
        value_str = str(getattr(instance, self.name, None))
        if not value_str.isdigit():
            self.not_valid_add_info = "not digit"
            return False
        if not (len(value_str) == 11):
            self.not_valid_add_info = "must be 11 digits"
            return False
        if not (value_str[0] == "7"):
            self.not_valid_add_info = "must start by '7'"
            return False
        return True

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        if isinstance(value, int):
            return True
        return isinstance(value, str) and value != ""


class DateField(CharField):
    pattern = r"^(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})$"
    template = re.compile(pattern)

    def get_date(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, str):
            self.not_valid_add_info = "not 'str' type"
            return None
        try:
            date = self.template.match(value)
            if not date:
                self.not_valid_add_info = "does not match 'DD.MM.YYYY' pattern"
                return None
            year, month, day = map(int, (date.group("year"), date.group("month"), date.group("day")))
            date = datetime.date(year, month, day)
        except:
            self.not_valid_add_info = "can't convert to date"
            return None
        return date

    def is_valid_value(self, instance):
        date = self.get_date(instance)
        if date is None:
            return False
        return True

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, str) and value != ""


class BirthDayField(DateField):
    pattern = r"^(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})$"
    template = re.compile(pattern)

    def is_valid_value(self, instance):
        if not super().is_valid_value(instance):
            return False
        date = self.get_date(instance)
        today = datetime.date.today()
        if (today - date) > (datetime.timedelta(days=365) * MAX_YEARS_FOR_BIRTHDAY):
            self.not_valid_add_info = f"Not older than {MAX_YEARS_FOR_BIRTHDAY} years"
            return False
        return True

    def is_not_empty_value(self, instance):
        return super().is_not_empty_value(instance)


class GenderField(Field):
    def is_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, int):
            self.not_valid_add_info = "not 'int' type"
            return False
        if value not in GENDERS:
            self.not_valid_add_info = "must by from <" + ", ".join(map(str, GENDERS.keys())) + ">"
            return False
        return True

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, int)


class ClientIDsField(Field):
    def is_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, list):
            self.not_valid_add_info = "not 'list' type"
            return False
        if not all(isinstance(x, int) for x in value):
            self.not_valid_add_info = "one or more element not 'int' type"
            return False
        return True

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, list) and value



# ====Coprocessor====

class Coprocessor:
    """
    If request class has other process classes then class must have attribute
    coprocessor = Coprocessor(<field containing value of coprocessor name>,
                              <field containing value of coprocessor arguments>)
    """

    def __init__(self, coprocessor_name, coprocessor_args):
        self.coprocessor_name = coprocessor_name
        self.coprocessor_args = coprocessor_args

    def __get__(self, instance, owner):
        if not hasattr(instance, "_coprocessors"):
            return None
        coprocessor_name = getattr(instance, self.coprocessor_name)
        if coprocessor_name not in instance._coprocessors:
            raise ValueError(f"coprocessor '{coprocessor_name}' not implemented")
        cls = instance._coprocessors[coprocessor_name]
        obj = cls.from_request(instance.ctx, instance.store, getattr(instance, self.coprocessor_args))
        obj.request = instance
        return obj


def coprocessor(processor):
    """
    Decorator for coprocessor classes
    If class is coprocessor for RequestClass, he must decorated
    @coprocessor(<RequestClass>)
    class CoprocessorClass(Request):
    """

    def wrapper(cls):
        if not hasattr(processor, "_coprocessors"):
            processor._coprocessors = {}
        processor._coprocessors[cls.coprocessor_name] = cls
        return cls
    return wrapper


# ====Request classes====

class MetaRequest(type):
    """
    Metaclass for request
    Add all declared fields objects to declared_fields class attribute and
    declared fields names to fields_name class attribute
    """

    def __new__(mcs, name, bases, dct):
        current_fields = []
        for k, v in list(dct.items()):
            if isinstance(v, Field):
                current_fields.append((k, v))
        fields = dict(current_fields)
        new_class = super().__new__(mcs, name, bases, dct)
        new_class.declared_fields = fields
        new_class.fields_name = fields.keys()
        return new_class


class Request(metaclass=MetaRequest):
    """
    Base class for request
    """

    @classmethod
    def from_request(cls, ctx, store, attrs):
        """return Request instance with seted attributes"""
        obj = cls(ctx, store)
        obj.set_attributes(attrs)
        return obj

    def __init__(self, ctx, store, need_validation=True, need_auth=False):
        self.ctx = ctx
        self.store = store
        self.need_validation = need_validation or True
        self.need_auth = need_auth or False

    def set_attributes(self, attrs):
        """set fields values"""
        for k, v in attrs.items():
            if k in self.fields_name:
                setattr(self, k, v)

    def validate(self):
        """
        validate fields values. In child may also have additional checks
        """

        invalid_fields = []
        for field_name, field in self.declared_fields.items():
            if not field.validate(self):
                invalid_fields.append(field_name)
        if invalid_fields:
            return validation_res(False, "Invalid fields: " + ", ".join(invalid_fields))

        return validation_res(True, "")

    def filled_fields(self):
        """
        return list of field names which has value
        """

        res = []
        for field_name, field in self.declared_fields.items():
            if field.is_not_empty_value(self):
                res.append(field_name)
        return res

    def process(self):
        """
        Process request
        If needed validate fields, check authenticate and run coprocessor
        """
        if self.need_validation:
            validation = self.validate()
            if not validation.is_valid:
                return validation.reason, INVALID_REQUEST

        if self.need_auth:
            if not check_auth(self):
                return ERRORS[FORBIDDEN], FORBIDDEN

        if hasattr(self, "coprocessor"):
            return self.coprocessor.process()

        return None


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    coprocessor = Coprocessor("method", "arguments")

    def __init__(self, ctx, store, need_validation=None, need_auth=None):
        need_validation = need_validation or True
        need_auth = need_auth or True
        super().__init__(ctx, store, need_validation, need_auth)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

"""
Coprocessor simple template

@coprocessor(MethodRequest)
class SimpleCoprocessor(Request):
    coprocessor_name = "simple"
    field1 = CharField(required=True, nullable=False)
    field2 = EmailField(required=True, nullable=False)


    def validate(self):
        base_validation = super().validate()
        if not base_validation.is_valid:
            return base_validation
        # check something
        if not (self.field1 == "42" and self.field2 == "admin@admin.admin"):
            return validation_res(False, "something wrong")
        return validation_res(True, "")

    def process(self):
        res = super().process()
        if res:
            return res
        # do something
        res = f"your choice is {self.field1}"
        return res, OK
"""

@coprocessor(MethodRequest)
class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)
    coprocessor_name = "clients_interests"

    def __init__(self, ctx, store, need_validation=None, need_auth=None):
        need_validation = need_validation or True
        need_auth = need_auth or False
        super().__init__(ctx, store, need_validation, need_auth)

    def process(self):
        res = super().process()
        if res:
            return res
        res = {}
        for id in self.client_ids:
            res[id] = get_interests(self.store, id)

        self.ctx["nclients"] = len(self.client_ids)
        return res, OK


@coprocessor(MethodRequest)
class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)
    coprocessor_name = "online_score"

    def __init__(self, ctx, store, need_validation=None, need_auth=None):
        need_validation = need_validation or True
        need_auth = need_auth or False
        super().__init__(ctx, store, need_validation, need_auth)

    def validate(self):
        base_validation = super().validate()
        if not base_validation.is_valid:
            return base_validation
        if (self.phone is None or self.email is None) and \
                (self.first_name is None or self.last_name is None) and \
                (self.gender is None or self.birthday is None):
            return validation_res(False, "One or more value pairs must be presents: "
                                         "'Phone - Email' or "
                                         "'First name - Last name' or "
                                         "'Gender - Birthday'")
        return validation_res(True, "")

    def process(self):
        res = super().process()
        if res:
            return res

        self.ctx["has"] = self.filled_fields()

        return {"score": 42 if self.request.is_admin else get_score(self.store, self.phone, self.email, self.birthday,
                                                                    self.gender, self.first_name, self.last_name)
                }, OK


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf8")).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode("utf8")).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    response, code = "OK", 200

    # method_request = MethodRequest(ctx, store)
    # method_request.set_attributes()

    method_request = MethodRequest.from_request(ctx, store, request["body"])
    return method_request.process()


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode("utf8"))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()