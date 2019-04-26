import tests.helpers.import_app

from tests.helpers.cases import cases as cases
import unittest
from app import api, scoring
import json


def init_field(field_cls, required=False, nullable=False):
        field = field_cls(required, nullable)
        return field


class TestCharField(unittest.TestCase):
    field_cls = api.CharField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate(None)
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "qqq"},
        {"value": "Привет"},
        {"value": """Hello,
                     request"""},

    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)

    @cases([
        {"value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": 123},
        {"value": [""]},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "qqq"},
        {"value": "Привет"},
        {"value": """Hello,
                           request"""},

    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)


class TestArgumentField(unittest.TestCase):
    field_cls = api.ArgumentsField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate(None)
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": {"qqq": "www"}},
        {"value": {"": "",
                   "qqq": 42}},

    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)

    @cases([
        {"value": {}},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": 123},
        {"value": [""]},
        {"value": "{qwe: '123'}"},

    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": {"qqq": "www"}},
        {"value": {"": "",
                   "qqq": 42}},

    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)


class TestEmailField(unittest.TestCase):
    field_cls = api.EmailField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate(None)
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "unit@test"},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)

    @cases([
        {"value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": 123},
        {"value": [""]},
        {"value": "email"},

    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "unit@test"},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)


class TestPhoneField(unittest.TestCase):
    field_cls = api.PhoneField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate(None)
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "79991234567"},

    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)

    @cases([
        {"value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "7999123456"},
        {"value": "799912345678"},
        {"value": "89991234567"},
        {"value": 7999123456},
        {"value": 799912345678},
        {"value": 89991234567},
        {"value": [79991234567]},

    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "79991234567"},
        {"value": 79991234567},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)


class TestDateField(unittest.TestCase):
    field_cls = api.DateField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate(None)
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "11.11.2011"},

    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)

    @cases([
        {"value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "2011.11.11"},
        {"value": ["11.11.2011"]},
        {"value": "11-11-2011"},
        {"value": "13.13.2013"},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "11.11.2011"}
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)


class TestBirthDayField(unittest.TestCase):
    field_cls = api.BirthDayField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate(None)
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "11.11.2011"},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)

    @cases([
        {"value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "2011.11.11"},
        {"value": ["11.11.2011"]},
        {"value": "11-11-2011"},
        {"value": "13.13.2013"},
        {"value": "11.11.1911"},
        {"value": "11.11.2111"},

    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": "11.11.2011"},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)


class TestGenderField(unittest.TestCase):
    field_cls = api.GenderField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate(None)
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": 1},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)

    @cases([
        {"value": ""},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": 12},
        {"value": "1"},
        {"value": [1]},

    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": 2},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)


class TestClientIdsField(unittest.TestCase):
    field_cls = api.ClientIDsField

    def test_invalid_required_field(self):
        field = init_field(self.field_cls, required=True)
        res = field.validate(None)
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": [1, 2]},
    ])
    def test_valid_required_field(self, arguments):
        field = init_field(self.field_cls, required=True)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)

    @cases([
        {"value": []},
    ])
    def test_invalid_not_nullable_field(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": [1, "2"]},
        {"value": ["1", "2"]},
        {"value": 1},
    ])
    def test_invalid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertFalse(res.is_valid)
        self.assertTrue(res.reason)

    @cases([
        {"value": [1, 2]},
        {"value": [1]},
    ])
    def test_valid_field_value(self, arguments):
        field = init_field(self.field_cls, nullable=False)
        res = field.validate(arguments["value"])
        self.assertTrue(res.is_valid)


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
