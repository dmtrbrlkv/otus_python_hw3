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
from store import Store

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
class FieldValidationError(Exception):
    pass


class Field(metaclass=ABCMeta):
    """
    Abstract class for fields
    All field classes must inherit from this class
    """

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable

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
    def check_valid_value(self, instance):
        """
        Raise FieldValidationError if value not valid
        Must present in child
        """

    def validate(self, instance):
        if self.required and getattr(instance, self.name, None) is None:
            return validation_res(False, f"field '{self.label}' is required")
        if not self.required and getattr(instance, self.name, None) is None:
            return validation_res(True, "")
        if not self.nullable and not self.is_not_empty_value(instance):
            return validation_res(False, f"field '{self.label}' is empty")
        try:
            self.check_valid_value(instance)
        except FieldValidationError as e:
            return validation_res(False, f"field '{self.label}', invalid value: {str(getattr(instance, self.name, None))} ({e})")
        return validation_res(True, "")


class CharField(Field):
    def check_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, str):
            raise FieldValidationError("not 'str' type")

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, str) and value != ""


class ArgumentsField(Field):
    def check_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, dict):
            raise FieldValidationError("not 'dict' type")

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, dict) and value


class EmailField(CharField):
    def check_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        super().check_valid_value(instance)
        if "@" not in value:
            raise FieldValidationError("'@' not present")

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, str) and value != ""


class PhoneField(Field):
    def check_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, (int, str)):
            raise FieldValidationError("not '(int, str)' type")

        value_str = str(getattr(instance, self.name, None))
        if not value_str.isdigit():
            raise FieldValidationError("not digit")
        if not (len(value_str) == 11):
            raise FieldValidationError("must be 11 digits")
        if not (value_str[0] == "7"):
            raise FieldValidationError("must start by '7'")

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
        date = self.template.match(value)
        year, month, day = map(int, (date.group("year"), date.group("month"), date.group("day")))
        return datetime.date(year, month, day)

    def check_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, str):
            raise FieldValidationError("not 'str' type")
        try:
            date = self.template.match(value)
            if not date:
                raise FieldValidationError("does not match 'DD.MM.YYYY' pattern")
            year, month, day = map(int, (date.group("year"), date.group("month"), date.group("day")))
            date = datetime.date(year, month, day)
        except:
            raise FieldValidationError("can't convert to date")

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, str) and value != ""

    def __get__(self, instance, owner):
        if self.is_not_empty_value(instance):
            return self.get_date(instance)
        return None


class BirthDayField(DateField):
    pattern = r"^(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})$"
    template = re.compile(pattern)

    def check_valid_value(self, instance):
        super().check_valid_value(instance)
        date = self.get_date(instance)
        today = datetime.date.today()
        if (today - date) > (datetime.timedelta(days=365) * MAX_YEARS_FOR_BIRTHDAY):
            raise FieldValidationError(f"Not older than {MAX_YEARS_FOR_BIRTHDAY} years")

    def is_not_empty_value(self, instance):
        return super().is_not_empty_value(instance)


class GenderField(Field):
    def check_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, int):
            raise FieldValidationError("not 'int' type")
        if value not in GENDERS:
            raise FieldValidationError("must by from <" + ", ".join(map(str, GENDERS.keys())) + ">")

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, int)


class ClientIDsField(Field):
    def check_valid_value(self, instance):
        value = getattr(instance, self.name, None)
        if not isinstance(value, list):
            raise FieldValidationError("not 'list' type")
        if not all(isinstance(x, int) for x in value):
            raise FieldValidationError("one or more element not 'int' type")

    def is_not_empty_value(self, instance):
        value = getattr(instance, self.name, None)
        return isinstance(value, list) and value


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
    def from_request(cls, attrs, request=None):
        """return Request instance with seted attributes"""
        obj = cls()
        obj.set_attributes(attrs)
        obj.request = request
        return obj

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
        invalid_reasons = []
        for field_name, field in self.declared_fields.items():
            res = field.validate(self)
            if not res.is_valid:
                invalid_fields.append(field_name)
                invalid_reasons.append(res.reason)
        if invalid_fields:
            return validation_res(False, "Invalid fields: " + ",".join(invalid_reasons))

        return validation_res(True, "")


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

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

    def filled_fields(self):
        """
        return list of field names which has value
        """

        res = []
        for field_name, field in self.declared_fields.items():
            if field.is_not_empty_value(self):
                res.append(field_name)
        return res


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf8")).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode("utf8")).hexdigest()
    if digest == request.token:
        return True
    return False


def process_method_request(request, ctx, store):
    methods_cls = {
        "clients_interests": ClientsInterestsRequest,
        "online_score": OnlineScoreRequest
    }

    methods_process = {
        "clients_interests": process_clients_interests_request,
        "online_score": process_online_score_interests_request
    }

    method = request.method
    if method not in methods_cls:
        raise NotImplementedError(f"Method {method} not implemented")

    sub_cls = methods_cls[method]
    sub_request = sub_cls.from_request(request.arguments, request)
    sub_process = methods_process[method]
    validation = sub_request.validate()
    if not validation.is_valid:
        return validation.reason, INVALID_REQUEST
    return sub_process(sub_request, ctx, store)


def process_clients_interests_request(request, ctx, store):
    res = {}
    for id in request.client_ids:
        res[id] = get_interests(store, id)

    ctx["nclients"] = len(request.client_ids)
    return res, OK


def process_online_score_interests_request(request, ctx, store):
    ctx["has"] = request.filled_fields()

    return {"score": 42 if request.request.is_admin else get_score(store, request.phone, request.email,
                                                                   request.birthday, request.gender, request.first_name,
                                                                   request.last_name)
            }, OK


def method_handler(request, ctx, store):
    method_request = MethodRequest.from_request(request["body"])
    validation = method_request.validate()
    if not validation.is_valid:
        return validation.reason, INVALID_REQUEST

    if not check_auth(method_request):
        return ERRORS[FORBIDDEN], FORBIDDEN

    return process_method_request(method_request, ctx, store)


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = Store()

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
