import os

from mongobar.exceptions import ConnectionNotSetError


class Connection(object):

    def __init__(self, root, name, host, port, \
            username=None, password=None, authdb=None):
        self.root = root
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.authdb = authdb

    @property
    def socket(self):
        return "{}:{}".format(self.host, self.port)

    @property
    def auth(self):
        return bool(self.username and self.password)

    @property
    def directory(self):
        return os.path.join(self.root, self.socket)


class Connections(object):

    def __init__(self):
        self.connections = {}

    def names(self, **kwargs):
        return [c for c in self.connections.keys()]

    def add(self, root, name, attributes):
        self.connections[name] = Connection(
            root,
            name,
            attributes.get("host"),
            attributes.get("port"),
            attributes.get("username", None),
            attributes.get("password", None),
            attributes.get("authdb", None)
        )

    def get(self, name=None, socket=None):

        # get by name
        if name is not None:
            if name not in self.connections:
                raise ConnectionNotSetError(name)
            return self.connections[name]

        # get by socket
        if socket is not None:
            for connection in self.connections.values():
                if connection.socket == socket:
                    return connection
