import tests.helpers.import_app
import unittest
from app import store
from tests.helpers.tarantool import get_tarantool_address as get_tarantool_address


class TestStoreIntegration(unittest.TestCase):
    def setUp(self):
        address = get_tarantool_address()
        if address:
            self.store = store.Store(*address)
        self.store_na = store.Store("###BadHost###")

    @unittest.skipIf(get_tarantool_address() is None, "Store not available")
    def test_available_store_get(self):
        store = self.store
        res = store.get("uid:bd9cece8db70c1d3af3661bf013ff5c6")
        self.assertEqual(res, "0.5")

    @unittest.skipIf(get_tarantool_address() is None, "Store not available")
    def test_available_cache_get(self):
        store = self.store
        store.cache_set("i:42", ["42"], 1)
        res = store.cache_get("i:42")
        self.assertEqual(res, "['42']")

    @unittest.skipIf(get_tarantool_address() is None, "Store not available")
    def test_available_cache_set(self):
        store = self.store
        self.assertTrue(store.cache_set("i:42", ["42"], 1))

    def test_not_available_store_get(self):
        store = self.store_na
        self.assertRaises(ConnectionError, store.get, "uid:bd9cece8db70c1d3af3661bf013ff5c6")

    def test_not_available_cache_get(self):
        store = self.store_na
        store.cache_set("i:42", ["42"], 1)
        res = store.cache_get("i:42")
        self.assertIsNone(res)

    def test_not_available_cache_set(self):
        store = self.store_na
        self.assertIsNone(store.cache_set("i:42", ["42"], 1))


if __name__ == "__main__":
    unittest.main()
