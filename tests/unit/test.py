# from os.path import dirname, join
# import sys
# sys.path.append(join(dirname(dirname(dirname(__file__))), "app"))
import tests.helpers.import_app

from tests.helpers.cases import cases as cases
import unittest
from app import api, store, scoring
import json


def init_field(field_cls, required=False, nullable=False, value=None):
        field = field_cls(required, nullable)
        if value is not None:
            field.set_value(value)
        return field


class TestCharField(unittest.TestCase):
    field_cls = api.CharField
    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)


class TestArgumentField(unittest.TestCase):
    field_cls = api.ArgumentsField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

class TestEmailField(unittest.TestCase):
    field_cls = api.EmailField
    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)


class TestPhoneField(unittest.TestCase):
    field_cls = api.PhoneField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)


class TestDateField(unittest.TestCase):
    field_cls = api.DateField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)


class TestBirthDayField(unittest.TestCase):
    field_cls = api.BirthDayField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)


class TestGenderField(unittest.TestCase):
    field_cls = api.GenderField
    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)


class TestClientIdsField(unittest.TestCase):
    field_cls = api.ClientIDsField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)


class TestCharField(unittest.TestCase):
    field_cls = api.CharField
    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)


class TestCharField(unittest.TestCase):
    field_cls = api.CharField
    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)

    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False, value=arguments["value"])
        res = field.validate()
        self.assertTrue(res.is_valid)




class TestFieldsSuite(unittest.TestCase):

    @cases([
        {"field_class": api.CharField},
        {"field_class": api.ArgumentsField},
        {"field_class": api.EmailField},
        {"field_class": api.PhoneField},
        {"field_class": api.DateField},
        {"field_class": api.BirthDayField},
        {"field_class": api.GenderField},
        {"field_class": api.GenderField},
        {"field_class": api.ClientIDsField},
    ])
    def test_invalid_required_field(self, arguments):
        field = arguments["field_class"](required=True)

        class Dummy(metaclass=api.MetaRequest):
            f = field

        dummy = Dummy()

        res = field.validate(dummy)
        self.assertFalse(res.is_valid, f"arguments = {arguments}")
        self.assertTrue(res.reason, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = arguments["field_class"](required=True)

        class Dummy(metaclass=api.MetaRequest):
            f = field

        dummy = Dummy()
        dummy.f = arguments["value"]

        res = field.validate(dummy)
        self.assertTrue(res.is_valid, f"arguments = {arguments}")


    @cases([
        {"field_class": api.CharField, "value": ""},
        {"field_class": api.ArgumentsField, "value": ""},
        {"field_class": api.EmailField, "value": ""},
        {"field_class": api.PhoneField, "value": ""},
        {"field_class": api.DateField, "value": ""},
        {"field_class": api.BirthDayField, "value": ""},
        {"field_class": api.GenderField, "value": ""},
        {"field_class": api.ClientIDsField, "value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = arguments["field_class"](nullable=False)

        class Dummy(metaclass=api.MetaRequest):
            f = field

        dummy = Dummy()
        dummy.f = arguments["value"]

        res = field.validate(dummy)
        self.assertFalse(res.is_valid, f"arguments = {arguments}")
        self.assertTrue(res.reason, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": "qqq"},
        {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
        {"field_class": api.EmailField, "value": "q@q"},
        {"field_class": api.PhoneField, "value": "79991234567"},
        {"field_class": api.DateField, "value": "21.04.2019"},
        {"field_class": api.BirthDayField, "value": "21.04.2000"},
        {"field_class": api.GenderField, "value": 1},
        {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_not_nullable_field(self, arguments):
        field = arguments["field_class"](nullable=False)

        class Dummy(metaclass=api.MetaRequest):
            f = field

        dummy = Dummy()
        dummy.f = arguments["value"]

        res = field.validate(dummy)
        self.assertTrue(res.is_valid, f"arguments = {arguments}")

    @cases([
        {"field_class": api.CharField, "value": 123},
        {"field_class": api.ArgumentsField, "value": "{'qqq': 'www'}"},
        {"field_class": api.EmailField, "value": "qqq"},
        {"field_class": api.PhoneField, "value": "7999123456"},
        {"field_class": api.PhoneField, "value": "89991234567"},
        {"field_class": api.PhoneField, "value": 7999123456},
        {"field_class": api.PhoneField, "value": 89991234567},
        {"field_class": api.DateField, "value": "33.04.2019"},
        {"field_class": api.DateField, "value": "2019.04.01"},
        {"field_class": api.DateField, "value": "04/01/1999"},
        {"field_class": api.BirthDayField, "value": "21.04.1920"},
        {"field_class": api.GenderField, "value": 5},
        {"field_class": api.GenderField, "value": "1"},
        {"field_class": api.ClientIDsField, "value": ["1", "2"]},
        {"field_class": api.ClientIDsField, "value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = arguments["field_class"](nullable=False)

        class Dummy(metaclass=api.MetaRequest):
            f = field

        dummy = Dummy()
        dummy.f = arguments["value"]

        res = field.validate(dummy)
        self.assertFalse(res.is_valid, f"arguments = {arguments}")
        self.assertTrue(res.reason, f"arguments = {arguments}")


    @cases([
            {"field_class": api.CharField, "value": "qqq"},
            {"field_class": api.ArgumentsField, "value": {"qqq": "www"}},
            {"field_class": api.EmailField, "value": "q@q"},
            {"field_class": api.PhoneField, "value": "79991234567"},
            {"field_class": api.DateField, "value": "21.04.2019"},
            {"field_class": api.BirthDayField, "value": "21.04.2000"},
            {"field_class": api.GenderField, "value": 1},
            {"field_class": api.ClientIDsField, "value": [1, 2]},
    ])
    def test_valid_field_value(self, arguments):
        field = arguments["field_class"](nullable=False)

        class Dummy(metaclass=api.MetaRequest):
            f = field

        dummy = Dummy()
        dummy.f = arguments["value"]

        res = field.validate(dummy)
        self.assertTrue(res.is_valid, f"arguments = {arguments}")


class MockAvailableStore:
    def __init__(self, cached_value=None):
        self.cached_value = cached_value

    def get(self, key):
        return json.dumps(["sport", "music"])

    def cache_get(self, key):
        return self.cached_value

    def cache_set(self, key, value, minutes):
        self.cached_value = value
        return True


class MockNotAvailableStore:
    def get(self, key):
        raise ConnectionError("Store not available")

    def cache_get(self, key):
        return None

    def cache_set(self, key, value, minutes):
        return False


class TestGetScoreSuite(unittest.TestCase):
    def test_get_score_available_store(self):
        store = MockAvailableStore()
        res = scoring.get_score(store, "79991234567", "q@q.q")
        self.assertIsInstance(res, float)

    def test_get_score_not_available_store(self):
        store = MockNotAvailableStore()
        res = scoring.get_score(store, "79991234567", "q@q.q")
        self.assertIsInstance(res, float)

    def test_get_score_from_cache(self):
        store = MockAvailableStore(cached_value=42)
        res = scoring.get_score(store, "79991234567", "q@q.q")
        self.assertEqual(res, 42)

    def test_get_score_save_cache(self):
        store = MockAvailableStore()
        res = scoring.get_score(store, "79991234567", "q@q.q")
        self.assertEqual(res, store.cached_value)


class TestGetInterestsScoreSuite(unittest.TestCase):
    def test_get_score_available_store(self):
        store = MockAvailableStore()
        res = scoring.get_interests(store, 1)
        self.assertIsInstance(res, list)

    def test_get_score_not_available_store(self):
        store = MockNotAvailableStore()
        self.assertRaises(ConnectionError, scoring.get_interests, store, 1)



if __name__ == "__main__":
    unittest.main()
