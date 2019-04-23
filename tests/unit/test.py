from os.path import dirname, join
import sys
sys.path.append(join(dirname(dirname(dirname(__file__))), "app"))


import hashlib
import datetime
import functools
import unittest

from app import api, store, scoring

import json

def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)
        return wrapper
    return decorator


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = store.Store()

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            request["token"] = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).encode("utf8")).hexdigest()
        else:
            msg = request.get("account", "") + request.get("login", "") + api.SALT
            request["token"] = hashlib.sha512(msg.encode("utf8")).hexdigest()

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "", "arguments": {}},
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "sdd", "arguments": {}},
        {"account": "horns&hoofs", "login": "admin", "method": "online_score", "token": "", "arguments": {}},
    ])
    def test_bad_auth(self, request):
        _, code = self.get_response(request)
        self.assertEqual(api.FORBIDDEN, code)

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
    ])
    def test_invalid_method_request(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code)
        self.assertTrue(len(response))

    @cases([
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": 1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "s", "last_name": 2},
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ])
    def test_invalid_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases([
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "a", "last_name": "b"},
    ])
    def test_ok_score_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code, arguments)
        score = response.get("score")
        self.assertTrue(isinstance(score, (int, float)) and score >= 0, arguments)
        self.assertEqual(sorted(self.context["has"]), sorted(arguments.keys()))

    def test_ok_score_admin_request(self):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        request = {"account": "horns&hoofs", "login": "admin", "method": "online_score", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code)
        score = response.get("score")
        self.assertEqual(score, 42)

    @cases([
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
    ])
    def test_invalid_interests_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases([
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ])
    def test_ok_interests_request(self, arguments):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "clients_interests", "arguments": arguments}
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(api.OK, code, arguments)
        self.assertEqual(len(arguments["client_ids"]), len(response))
        # self.assertTrue(all(v and isinstance(v, list) and all(isinstance(i, basestring) for i in v)
        #                 for v in response.values()))
        self.assertTrue(all(v and isinstance(v, list) and all(isinstance(i, str) for i in v)
                         for v in response.values()), arguments)

        self.assertEqual(self.context.get("nclients"), len(arguments["client_ids"]))


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
