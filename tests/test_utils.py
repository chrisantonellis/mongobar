
import sys; sys.path.append("../") # noqa
import unittest
import os
import subprocess

from unittest import mock

import mongobar.utils as utils


# Test Utility Methods

class TestUtils(unittest.TestCase):

    # _merge

    def test___merge(self):
        input_1 = {"a": "v"}
        input_2 = {"b": "v"}
        output = utils._merge(input_1, input_2)
        expected_output = {"a": "v", "b": "v"}

        self.assertEqual(output, expected_output)
        self.assertEqual(input_2, expected_output)

    def test___merge__recursive(self):
        input_1 = {"a": {"b": "v1"}}
        input_2 = {"a": {"b": "v2"}}
        output = utils._merge(input_1, input_2)
        expected_output = {"a": {"b": "v1"}}

        self.assertEqual(output, expected_output)
        self.assertEqual(input_2, expected_output)

    # merge

    def test__merge(self):
        input_1 = {"a": "v"}
        input_2 = {"b": "v"}
        output = utils.merge(input_1, input_2)
        expected_output = {"a": "v", "b": "v"}

        self.assertEqual(output, expected_output)
        self.assertNotEqual(input_2, expected_output)


    # get_directories

    @mock.patch("mongobar.utils.os.path.isdir", return_value=True)
    @mock.patch("mongobar.utils.os.listdir", return_value=["subdirectory"])
    def test___get_directories(self, listdir, isdir):
        utils.get_directories("test")
        listdir.assert_called_with("test")
        isdir.assert_called_with("test/subdirectory")

    @mock.patch("mongobar.utils.os.path.isdir", return_value=True)
    @mock.patch("mongobar.utils.os.listdir", side_effect=Exception())
    def test___get_directories__raises_Exception(self, listdir, isdir):
        with self.assertRaises(Exception):
            utils.get_directories("test")

    # create_directory

    @mock.patch("mongobar.utils.os.makedirs", return_value=True)
    def test___create_directory(self, makedirs):
        utils.create_directory("test/subdirectory/")
        makedirs.assert_called_with("test/subdirectory/")

    @mock.patch("mongobar.utils.os.makedirs", side_effect=Exception())
    def test___create_directory__raises_Exception(self, makedirs):
        with self.assertRaises(Exception):
            utils.create_directory("test/subdirectory/")
