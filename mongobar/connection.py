import os

from mongobar.exceptions import ConnectionNotSetError
from mongobar.exceptions import ConnectionAttributeNotSetError
from mongobar.exceptions import ConnectionAuthdbSetError


class Connection(object):

    def __init__(self, name, host, port, username=None, password=None, \
            authdb=None):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.authdb = authdb

    def validate(self):

        if not all(getattr(self, k) is not None for k in ["host", "port"]):
            raise ConnectionAttributeNotSetError(k)

        if any(getattr(self, k) is not None for k in ["username", "password"]):

            if not all(getattr(self, k) is not None for k in ["username", "password"]):
                raise ConnectionAttributeNotSetError(k)

        elif self.authdb is not None:
            raise ConnectionAuthdbSetError

        return self

    @property
    def socket(self):
        return "{}:{}".format(self.host, self.port)

    @property
    def auth(self):
        return bool(self.username and self.password)


class Connections(object):

    def __init__(self):
        self.connections = {}

    def names(self, **kwargs):
        return [c for c in self.connections.keys()]

    def add(self, name, data):
        self.connections[name] = Connection(
            name,
            data.get("host"),
            data.get("port"),
            data.get("username", None),
            data.get("password", None),
            data.get("authdb", None)
        )

    def get(self, name=None, socket=None):

        # get by name
        if name is not None:
            if name not in self.connections:
                raise ConnectionNotSetError(name)
            return self.connections[name].validate()

        # get by socket
        if socket is not None:
            for connection in self.connections.values():
                if connection.socket == socket:
                    return connection.validate()
