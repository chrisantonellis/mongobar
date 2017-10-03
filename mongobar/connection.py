import os

from mongobar.exceptions import ConnectionNotSetError
from mongobar.exceptions import ConnectionAttributeNotSetError


class Connection(object):

    def __init__(self, name, host=None, port=None, \
            username=None, password=None, authdb=None):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.authdb = authdb

    def validate(self):

        # host
        if self.host is None:
            raise ConnectionAttributeNotSetError("host")

        # port
        if self.port is None:
            raise ConnectionAttributeNotSetError("port")

        # username, password
        if self.username is not None or self.password is not None:

            if self.username is None:
                raise ConnectionAttributeNotSetError("username")

            if self.password is None:
                raise ConnectionAttributeNotSetError("password")

        return True

    @property
    def socket(self):
        return "{}:{}".format(self.host, self.port)

    @property
    def auth(self):
        return bool(self.username and self.password)

    def get(self):

        self.validate()

        data = {
            "host": self.host,
            "port": self.port
        }

        if self.username is not None:
            data["username"] = self.username
            data["password"] = self.password

        if self.authdb is not None:
            data["authdb"] = self.authdb

        return data


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

            connection = self.connections[name]
            connection.validate()
            return connection

        # get by socket
        if socket is not None:
            for connection in self.connections.values():
                if connection.socket == socket:

                    connection.validate()
                    return connection
