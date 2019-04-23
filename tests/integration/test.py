from os.path import dirname, join
import sys
sys.path.append(join(dirname(dirname(dirname(__file__))), "app"))


import hashlib
import datetime
import functools
import unittest

from app import api, store

import json
import subprocess
import requests
from os.path import dirname
import os.path
import time


class TestAvailableStoreIntegration(unittest.TestCase):
    def setUp(self):
        d = subprocess.Popen(["docker", "start", "mytarantool"])
        d.wait(2)
        time.sleep(2)


    def tearDown(self):
        d = subprocess.Popen(["docker", "stop", "mytarantool"])
        d.wait(2)
        time.sleep(2)

    def test_store_get(self):
        mstore = store.Store()
        res = mstore.get("uid:bd9cece8db70c1d3af3661bf013ff5c6")
        self.assertEqual(res, "0.5")

    def test_cache_get(self):
        mstore = store.Store()
        mstore.cache_set("i:42", ["42"], 1)
        res = mstore.cache_get("i:42")
        self.assertEqual(res, "['42']")

    def test_cache_set(self):
        mstore = store.Store()
        self.assertTrue(mstore.cache_set("i:42", ["42"], 1))



class TestNotAvailableStoreIntegration(unittest.TestCase):
    def setUp(self):
        d = subprocess.Popen(["docker", "stop", "mytarantool"])
        d.wait(2)
        time.sleep(2)

    def test_store_get(self):
        mstore = store.Store()
        self.assertRaises(ConnectionError, mstore.get, "uid:bd9cece8db70c1d3af3661bf013ff5c6")

    def test_cache_get(self):
        mstore = store.Store()
        mstore.cache_set("i:42", ["42"], 1)
        res = mstore.cache_get("i:42")
        self.assertIsNone(res)

    def test_cache_set(self):
        mstore = store.Store()
        self.assertIsNone(mstore.cache_set("i:42", ["42"], 1))


class TestFunctional(unittest.TestCase):
    def setUp(self):

        dir = dirname(dirname(dirname(__file__)))
        api_dir = os.path.join(dir, "app")
        print(api_dir)

        os.chdir(api_dir)
        p = subprocess.Popen(["python", "api.py", "-p", "8080"])
        self.p = p
        d = subprocess.Popen(["docker", "start", "mytarantool"])

    def tearDown(self):
        self.p.kill()
        subprocess.Popen(["docker", "stop", "mytarantool"])
        os.chdir(dirname(__file__))

    def test_clients_interests_requset(self):
        headers = {"Content-Type": "application/json"}
        data = """{
                "account": "horns&hoofs",
                "login": "h&f",
                "method": "clients_interests",
                "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
                "arguments": {
                    "client_ids": [
                        1,
                        2,
                        3,
                        4
                    ],
                    "date": "20.07.2017"
                }
        }""".encode("utf8")

        response = requests.post("http://localhost:8080/method", data=data, headers=headers)
        self.assertEqual(response.status_code, api.OK)
        data = response.json()
        self.assertEqual(data["response"]["2"],  ["sport", "cars"])

    def test_score_requset(self):
        headers = {"Content-Type": "application/json"}
        data = """{
                "account": "horns&hoofs",
                "login": "h&f",
                "method": "online_score",
                "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
                "arguments": {
                    "phone": "79175002040",
                    "email": "stupnikov@otus.ru",
                    "first_name": "Стансилав",
                    "last_name": "Ступников",
                    "birthday": "01.01.1990",
                    "gender": 1
                }
        }""".encode("utf8")
        response = requests.post("http://localhost:8080/method", data=data, headers=headers)
        self.assertEqual(response.status_code, api.OK)
        data = response.json()
        self.assertEqual(data["response"]["score"], 5.0)


if __name__ == "__main__":
    unittest.main()
