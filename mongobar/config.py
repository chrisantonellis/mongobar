import os
import logging
import json
import copy

from mongobar.connection import Connection
from mongobar.connection import Connections
from mongobar.exceptions import ConnectionNotSetError
from mongobar.utils import merge


class Config(object):

    default_connection = "default"
    default_config = {
        "root": "~/.mongobar_backups",
        "log_level": "INFO",
        "connections": {
            "default": {
                "host": "localhost",
                "port": 27017
            }
        }
    }

    def __init__(self):
        self.logger = logging.getLogger("mongobar_config")
        self._connection = self.default_connection
        self.connections = Connections()
        self.configs = [self.default_config]
        self.config = {}
        self.merge()

    @property
    def connection(self):
        return self.connections.get(self._connection)

    @connection.setter
    def connection(self, value):
        self._connection = value

    @property
    def connection_dir(self):
        return os.path.join(self.root, self.connection.socket)

    @property
    def root(self):
        return os.path.expanduser(self.config.get("root"))

    @property
    def log_level(self):
        return self.config.get("log_level", None)

    @property
    def log_file(self):
        return self.config.get("log_file", None)

    def add(self, data):
        self.configs.append(data)
        self.merge()

    def add_file(self, config_file):
        try:
            with open(os.path.expanduser(config_file)) as file_handle:
                self.add(json.loads(file_handle.read()))
            self.merge()
        except Exception as e:
            # print(e)
            pass

    def merge(self):
        data = {}

        # merge configs
        for layer in self.configs:
            data = merge(layer, data)
        self.config = copy.deepcopy(data)

        # create connections
        self.connections.connections = {}
        for name, attributes in data["connections"].items():
            self.connections.add(name, attributes)
