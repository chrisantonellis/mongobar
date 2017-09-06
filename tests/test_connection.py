import sys; sys.path.append("../") # noqa
import unittest
import logging

from unittest import mock

from mongobar.connection import Connection
from mongobar.connection import Connections

from mongobar.exceptions import ConnectionNotSetError
from mongobar.exceptions import ConnectionAttributeNotSetError


# Test Connection

class TestConnection(unittest.TestCase):

    # validate

    def test__validate(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017
        )

        self.assertTrue(c.validate())

    def test__validate__auth_args(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017,
            username="username",
            password="password",
            authdb="authdb"
        )

        self.assertTrue(c.validate())

    def test__validate__missing_host__raises__ConnectionAttributeNotSetError(self):
        c = Connection(
            name="default",
            port=27017
        )

        with self.assertRaises(ConnectionAttributeNotSetError):
            c.validate()

    def test__validate__missing_port__raises__ConnectionAttributeNotSetError(self):
        c = Connection(
            name="default",
            host="localhost"
        )

        with self.assertRaises(ConnectionAttributeNotSetError):
            c.validate()

    def test__validate__missing_username__raises__ConnectionAttributeNotSetError(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017,
            password="pass"
        )

        with self.assertRaises(ConnectionAttributeNotSetError):
            c.validate()

    def test__validate__missing_password__raises__ConnectionAttributeNotSetError(self):
        c = Connection(
            name="default",
            host="localhost",
            port=27017,
            username="user"
        )

        with self.assertRaises(ConnectionAttributeNotSetError):
            c.validate()

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
