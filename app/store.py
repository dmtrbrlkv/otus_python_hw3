import tarantool
import logging
import datetime
import json
import time


class Store:
    def __init__(self, host="localhost", port=3301, user=None, password=None, reconnect_n=10, reconnect_delay=1,
                 timeout=5, log=None):
        self.host = host
        self.port = port
        self.reconnect_n = reconnect_n
        self.reconnect_delay = reconnect_delay
        self.connection = tarantool.Connection(host, port,
                                               user=user,
                                               password=password,
                                               connect_now=False,
                                               connection_timeout=timeout)
        self.log = log or logging

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
        attempt = 0
        while attempt < self.reconnect_n:
            try:
                return self.try_get(key)
            except tarantool.error.NetworkError as e:
                attempt += 1
                self.reconnect_after_error(e, attempt)

        raise ConnectionError("Unable connect to the store")

    def cache_get(self, key):
        id = self.get_id(key)
        try:
            space = self.get_space(key)
            response = space.select(id)
            if not response.data:
                return None
            if len(response.data[0]) < 2:
                return None
            value = response.data[0][1]
            valid_thru = response.data[0][2]
            if not valid_thru:
                return None
            valid_thru = datetime.datetime.fromisoformat(valid_thru)
            if valid_thru < datetime.datetime.today():
                return None
            if isinstance(value, list):
                return str(value)
            return value
        except Exception as e:
            self.log.warning(f"Error getting data from cache - {e}")
            return None

    def cache_set(self, key, value, minutes):
        attempt = 0
        while attempt < self.reconnect_n:
            try:
                return self.try_cache_set(key, value, minutes)
            except tarantool.error.NetworkError as e:
                attempt += 1
                self.reconnect_after_error(e, attempt)
                error = str(e)

        self.log.warning(f"Error saving data to cache - {error}")
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

    def reconnect_after_error(self, e, attempt):
        self.log.info(f"connection error - {e}, reconnecting after {self.reconnect_delay} seconds, "
                      f"attempt {attempt} of {self.reconnect_n}")
        time.sleep(self.reconnect_delay)
        self.connect()

    def try_get(self, key):
        id = self.get_id(key)
        if id is None:
            raise ValueError("Invalid key")
        space = self.get_space(key)
        response = space.select(id)
        if not response.data:
            return json.dumps([""])
        value = response.data[0][1]
        return json.dumps(value)

    def try_cache_set(self, key, value, minutes):
        id = self.get_id(key)
        if id is None:
            raise ValueError("Invalid key")
        space = self.get_space(key)
        response = space.select(id)
        valid_thru = datetime.datetime.today() + datetime.timedelta(minutes=minutes)
        valid_thru = valid_thru.isoformat()

        if not response.data:
            space.insert((id, value, valid_thru))
        else:
            space.update(id, [("=", 1, value), ("=", 2, valid_thru)])
        return True

