import tarantool
import logging
import datetime
import json


class Store:
    def __init__(self, host="localhost", port=3301, user=None, password=None, reconnect_n=10, reconnect_delay=1, log=None):
        self.host = host
        self.port = port
        self.reconnect_n = reconnect_n
        self.reconnect_delay = reconnect_delay
        self.connection = tarantool.Connection(host, port,
                                               user=user,
                                               password=password,
                                               connect_now=False)
        self.log = log or logging
        self.cache_valid_thru = {}
        self.attempt = 0

    @staticmethod
    def get_id(key):
        if key.startswith("uid:"):
            return key[4:]
        if key.startswith("i:"):
            return int(key[2:])
        else:
            return None

    def get_space(self, key):
        if key.startswith("uid:"):
            return self.connection.space('scoring')
        elif key.startswith("i:"):
            return self.connection.space('interests')
        else:
            return None

    def get(self, key):
        id = self.get_id(key)
        if id is None:
            raise ValueError("Invalid key")
        self.attempt = self.attempt or 0
        try:
            space = self.get_space(key)
            response = space.select(id)
            self.attempt = 0
            if not response.data:
                return json.dumps([""])
            value = response.data[0][1]
            return json.dumps(value)
        except tarantool.error.NetworkError as e:
            self.attempt += 1
            while self.attempt <= self.reconnect_n:
                self.log.info(f"connection error - {e}, reconnecting after {self.reconnect_delay} seconds, "
                              f"attempt {self.attempt} of {self.reconnect_n}")
                next_try = datetime.datetime.today() + datetime.timedelta(seconds=self.reconnect_delay)
                while datetime.datetime.today() < next_try:
                    pass
                if self.connect():
                    return self.get(key)
                self.attempt += 1
            else:
                raise ConnectionError(e)

    def cache_get(self, key):
        id = self.get_id(key)
        if id is None or key not in self.cache_valid_thru or self.cache_valid_thru[key] < datetime.datetime.today():
            return None
        try:
            space = self.get_space(key)
            response = space.select(id)
            if not response.data:
                return None
            value = response.data[0][1]
            if isinstance(value, list):
                return str(value)
            return value
        except Exception as e:
            self.log.warning(f"Error getting data from cache - {e}")
            return None

    def cache_set(self, key, value, minutes):
        id = self.get_id(key)
        try:
            space = self.get_space(key)
            response = space.select(id)
            if not response.data:
                space.insert((id, value))
            else:
                space.update(id, [("=", 1, value)])
            self.cache_valid_thru[key] = datetime.datetime.today() + datetime.timedelta(minutes=minutes)
            return True
        except Exception as e:
            self.log.warning(f"Error saving data to cache - {e}")
            return None

    def connect(self):
        try:
            self.log.info(f"connecting to {self.host}: {self.port} ...")
            self.connection.connect()
        except Exception as e:
            self.log.warning(f"connection error - {e}")
            return False
        self.log.info("connected")
        return True

#
# store = Store()
# store.connect()
#
# for i in range(10):
#     res = store.cache_get("uid:www")
#     print(res)
#     res = 42
#     store.cache_set("uid:www", res, 10)
#
#     res = store.cache_get("i:1")
#     print(res)
#     res = ["music"]
#     store.cache_set("i:1", res, 10)
#
#     res = store.cache_get("i:2")
#     res = ["sport", "cars"]
#     print(res)
#     store.cache_set("i:2", res, 10)
#
#     time.sleep(2)
