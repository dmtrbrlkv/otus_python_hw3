import os


def get_tarantool_address():
    address = os.environ.get("TARANTOOL_ADDRESS")
    port = os.environ.get("TARANTOOL_PORT")
    if not (address and port):
        return None
    return address, port
