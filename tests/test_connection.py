import sys; sys.path.append("../") # noqa
import unittest
import logging

from unittest import mock

from mongobar.connection import Connection
from mongobar.connection import Connections

from mongobar.exceptions import ConnectionNotSetError


# Test Connection

class TestConnection(unittest.TestCase):

    # host

    def test__host_property(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017
        )

        self.assertEqual(c.host, "localhost")

    # port

    def test__port_property(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017
        )

        self.assertEqual(c.port, 27017)

    # username

    def test__username_property__returns_value(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017,
            username="user",
            password="password",
            authdb="authdb"
        )

        self.assertEqual(c.username, "user")

    # password

    def test__password_property__returns_value(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017,
            username="user",
            password="password",
            authdb="authdb"
        )

        self.assertEqual(c.password, "password")

    # authdb

    def test__authdb_property__returns_value(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017,
            username="user",
            password="password",
            authdb="authdb"
        )

        self.assertEqual(c.authdb, "authdb")

    # socket

    def test__socket_property(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017
        )

        self.assertEqual(c.socket, "localhost:27017")

    # auth

    def test__auth__returns_False(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017
        )

        self.assertFalse(c.auth)

    def test__auth__returns_True(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017,
            username="user",
            password="password",
        )

        self.assertTrue(c.auth)

    # def test__directory_property(self):
    #     c = Connection(
    #         name="default",
    #         host="localhost",
    #         port=27017
    #     )
    #
    #     self.assertEqual(c.directory, "/localhost:27017")


class TestConnections(unittest.TestCase):

    def test____init____no_args(self):
        c = Connections()
        self.assertEqual(c.connections, {})

    def test__names(self):
        c = Connections()
        c.add("foo", {"host": "bar", "port": 27017})
        c.add("bar", {"host": "bar", "port": 27017})
        self.assertEqual(c.names(), ["foo", "bar"])

    def test__add(self):
        c = Connections()
        c.add("foo", {"host": "bar", "port": 27017})
        self.assertEqual(c.connections["foo"].name, "foo")
        self.assertEqual(c.connections["foo"].host, "bar")
        self.assertEqual(c.connections["foo"].port, 27017)

    def test__get__name_arg(self):
        c = Connections()
        c.add("foobar", {"host": "localhost", "port": 27017})
        connection = c.get("foobar")
        self.assertEqual(connection.host, "localhost")
        self.assertEqual(connection.port, 27017)

    def test__get__name_arg__raises_ConnectionNotSetError(self):
        c = Connections()
        with self.assertRaises(ConnectionNotSetError):
            c.get("foobar")

    def test__get__socket_arg(self):
        c = Connections()
        c.add("foobar", {"host": "localhost", "port": 27017})
        self.assertEqual(c.get(socket="localhost:27017").name, "foobar")
