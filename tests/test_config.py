import sys; sys.path.append("../") # noqa
import unittest
import logging

from unittest import mock

import mongobar


mocked_config_1 = {
    "root": "/backups",
    "connections": {
        "default": {
            "host": "localhost",
            "port": 27017
        }
    }
}

mocked_config_2 = {
    "log_level": "DEBUG",
    "connections": {
        "custom": {
            "host": "custom",
            "port": 27017
        }
    }
}

# Test Config

class TestConfig(unittest.TestCase):

    # init

    def test____init____no_args(self):
        m = mongobar.Config()
        self.assertIsInstance(m.connections, mongobar.connection.Connections)
        self.assertEqual(m.configs, [m.default_config])
        self.assertIsInstance(m.logger, logging.Logger)

    # add_data

    def test__add_data(self):
        m = mongobar.Config()
        m.add(mocked_config_1)
        self.assertEqual(m.configs, [m.default_config, mocked_config_1])

    # add_file

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("mongobar.mongobar.json.loads", return_value=mocked_config_1)
    def test__add_file(self, loads, open_):
        m = mongobar.Config()
        m.add_file("/file.json")
        open_.assert_called_with("/file.json")
        self.assertEqual(m.configs, [m.default_config, mocked_config_1])

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("mongobar.mongobar.json.loads", side_effect=Exception())
    def test__add_file__does_not_raise_exception(self, loads, open_):
        m = mongobar.Config()
        m.add_file("/file.json")

    # root

    def test__root_property(self):
        m = mongobar.Config()
        self.assertEqual(m.root, "/root/.mongobar_backups")

    # log_level

    def test__log_level_property(self):
        m = mongobar.Config()
        self.assertEqual(m.log_level, "INFO")

    # log_file

    def test__log_file_property(self):
        m = mongobar.Config()
        m.add({"log_file": "/logfile"})
        self.assertEqual(m.log_file, "/logfile")
