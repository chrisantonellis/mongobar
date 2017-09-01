
import sys; sys.path.append("../") # noqa
import unittest
import logging
import os
import subprocess
import datetime
import pymongo

from unittest import mock

import mongobar


# Mocked Mongo Client


class MockedMongoDocument(mock.Mock):
    pass


class MockedMongoCollection(mock.Mock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mocked_documents = [
            MockedMongoDocument(),
            MockedMongoDocument(),
            MockedMongoDocument()
        ]

    def count(self):
        return len(self._mocked_documents)


class MockedMongoDatabase(mock.Mock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mocked_collections = {
            "c1": MockedMongoCollection(),
            "c2": MockedMongoCollection(),
            "c3": MockedMongoCollection(),
        }

    def __getitem__(self, key):
        return self._mocked_collections[key]

    def collection_names(self):
        return [key for key in self._mocked_collections.keys()]


class MockedMongoClient(mock.Mock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mocked_databases = {
            "local": MockedMongoDatabase(),
            "d1": MockedMongoDatabase(),
            "d2": MockedMongoDatabase(),
            "d3": MockedMongoDatabase(),
        }

    def __getitem__(self, key):
        return self._mocked_databases[key]

    def database_names(self):
        return [key for key in self._mocked_databases.keys()]


# Mocked Backup Metadata


MOCKED_BACKUP_METADATA_1_DB = {
    "host": "localhost",
    "port": 27017,
    "date": datetime.datetime.today().isoformat(),
    "databases": [{
        "name": "d1",
        "collections": [{
            "name": "c1",
            "document_count": 1
        },{
            "name": "c2",
            "document_count": 1
        },
        {
            "name": "c3",
            "document_count": 1
        }]
    }]
}

MOCKED_BACKUP_METADATA_3_DBS = {
    "host": "localhost",
    "port": 27017,
    "date": datetime.datetime.today().isoformat(),
    "databases": [{
        "name": "d1",
        "collections": [{
            "name": "c1",
            "document_count": 1
        },{
            "name": "c2",
            "document_count": 1
        },
        {
            "name": "c3",
            "document_count": 1
        }]
    },{
        "name": "d2",
        "collections": [{
            "name": "c1",
            "document_count": 1
        },{
            "name": "c2",
            "document_count": 1
        },
        {
            "name": "c3",
            "document_count": 1
        }]
    },{
        "name": "d3",
        "collections": [{
            "name": "c1",
            "document_count": 1
        },{
            "name": "c2",
            "document_count": 1
        },
        {
            "name": "c3",
            "document_count": 1
        }]
    }]
}


# Test Mongobar Package


@mock.patch("mongobar.mongobar.pymongo.MongoClient", new_callable=MockedMongoClient)
class TestMongobar(unittest.TestCase):

    # generate_backup_name

    @mock.patch("mongobar.mongobar.pkgutil.get_data", side_effect=[b"foo", b"bar"])
    def test__generate_backup_name(self, *args):
        name = mongobar.Mongobar().generate_backup_name()
        self.assertEqual(name, "foo-bar")
        args[0].assert_called()

    # create_pymongo_client

    def test__create_pymongo_client__default_connection(self, mongoclient):
        m = mongobar.Mongobar()
        m.create_pymongo_client()
        mongoclient.assert_called_with(
            host="localhost",
            port=27017
        )

    def test__create_pymongo_client__custom_connection(self, mongoclient):
        m = mongobar.Mongobar()
        m.config.add({
            "connections": {
                "custom": {
                    "host": "custom",
                    "port": 27017
                }
            }
        })
        m.config.connection = "custom"
        m.create_pymongo_client()
        mongoclient.assert_called_with(
            host="custom",
            port=27017
        )

    def test__create_pymongo_client__auth_options(self, mongoclient):
        m = mongobar.Mongobar()
        m.config.add({
            "connections": {
                "default": {
                    "host": "localhost",
                    "port": 27017,
                    "username": "user",
                    "password": "pass",
                    "authdb": "authdb"
                }
            }
        })
        m.create_pymongo_client()
        mongoclient.assert_called_with(
            host="localhost",
            port=27017,
            username="user",
            password="pass",
            authSource="authdb"
        )

    # generate_metadata

    def test__generate_metadata__databases_arg(self, mongoclient):
        m = mongobar.Mongobar()

        metadata = m.generate_metadata(databases=["d1", "d2", "d3"])

        self.assertIn("host", metadata)
        self.assertIn("port", metadata)
        self.assertIn("date", metadata)
        self.assertIn("databases", metadata)

        for database in metadata["databases"]:
            self.assertIn("name", database)
            self.assertIn("collections", database)

    def test__generate_metadata__databases_arg__remove_local(self, mongoclient):
        m = mongobar.Mongobar()
        metadata = m.generate_metadata(databases=["d1", "d2", "d3", "local"])
        self.assertNotIn("local", metadata["databases"])

    # write_metadata

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("mongobar.mongobar.json.dump")
    def test__write_metadata(self, dump, open_, mongoclient):
        m = mongobar.Mongobar()
        m.write_metadata("name", {"key": "value"})

        path = os.path.join(
            m.config.connection.directory,
            "name",
            "metadata.json"
        )
        open_.assert_called_with(path, "w+")

        file_handle = open_()
        dump.assert_called_with({"key": "value"}, file_handle)

    # read_metadata

    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("mongobar.mongobar.json.loads")
    def test__read_metadata(self, loads, open_, mongoclient):

        m = mongobar.Mongobar()
        m.read_metadata("name")

        path = os.path.join(
            m.config.connection.directory,
            "name",
            "metadata.json"
        )
        open_.assert_called_with(path, "r")

        file_handle = open_()
        file_handle.read.assert_called()

        loads.assert_called_with("")

    @mock.patch("builtins.open", side_effect=FileNotFoundError())
    @mock.patch("mongobar.mongobar.json.loads")
    def test__read_metadata__file_not_found(self, loads, open_, mongoclient):
        m = mongobar.Mongobar()
        self.assertEqual(m.read_metadata("name"), {
            "host": "localhost",
            "port": 27017,
            "date": "0001-01-01T00:00:00.0000",
            "databases": [],
            "message": "Metadata not found"
        })

    # backup

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    def test__backup(self, check_output, *args):
        m = mongobar.Mongobar()
        m.backup()

        directory = os.path.join(m.config.connection.directory, "foo-bar")

        self.assertIn(
            mock.call([
                "mongodump",
                "-h", "localhost",
                "-p", "27017",
                "--db", "d1",
                "--out", directory,
                "--quiet",
                "--gzip"
            ]),
            check_output.call_args_list
        )

    @mock.patch("mongobar.mongobar.os.path.exists", side_effect=[False, True])
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    def test__backup__create_root_directory(self, *args):
        m = mongobar.Mongobar()
        m.backup()
        self.assertIn(mock.call(m.config.root), args[3].call_args_list)

    @mock.patch("mongobar.mongobar.os.path.exists", side_effect=[True, False])
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    def test__backup__create_host_directory(self, *args):
        m = mongobar.Mongobar()
        m.backup()
        self.assertIn(mock.call(m.config.connection.directory), args[3].call_args_list)

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=False)
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    def test__backup__message_arg(self, *args):
        m = mongobar.Mongobar()
        m.backup(message="foo")

        # extract metadata arg passed to self.write_metadata
        write_metadata_mock = args[1]
        write_metadata_calls = write_metadata_mock.call_args_list[0]
        write_metadata_args = write_metadata_calls[0]
        metadata = write_metadata_args[1]

        self.assertEqual(metadata["message"], "foo")

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    def test__backup__auth_args(self, *args):

        m = mongobar.Mongobar()
        m.config.add({
            "connections": {
                "default": {
                    "host": "localhost",
                    "port": 27017,
                    "username": "user",
                    "password": "pass",
                    "authdb": "authdb"
                }
            }
        })
        m.backup()

        self.assertIn(
            mock.call([
                "mongodump",
                "-h", "localhost",
                "-p", "27017",
                "-u", "user",
                "-p", "pass",
                "--authenticationDatabase", "authdb",
                "--db", "d1",
                "--out", os.path.join(m.config.connection.directory, "foo-bar"),
                "--quiet",
                "--gzip"
            ]),
            args[0].call_args_list
        )

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    def test__backup__db_does_not_exist__command_called(self, check_output, *args):

        m = mongobar.Mongobar()
        m.backup(databases=["foobar"])

        self.assertIn(
            mock.call([
                "mongodump",
                "-h", "localhost",
                "-p", "27017",
                "--db", "foobar",
                "--out", os.path.join(m.config.connection.directory, "foo-bar"),
                "--quiet",
                "--gzip"
            ]),
            check_output.call_args_list
        )

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output", side_effect=[subprocess.CalledProcessError(1, "")])
    def test__backup__db_arg__raises_CalledProcessError(self, check_output, *args):
        m = mongobar.Mongobar()
        with self.assertRaises(mongobar.exceptions.CommandError):
            m.backup()

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    def test__backup__collection_arg(self, check_output, *args):

        m = mongobar.Mongobar()
        m.backup(databases=["d1"], collections=["c1"])

        self.assertIn(
            mock.call([
                "mongodump",
                "-h", "localhost",
                "-p", "27017",
                "--db", "d1",
                "--collection", "c1",
                "--out", os.path.join(m.config.connection.directory, "foo-bar"),
                "--quiet",
                "--gzip"
            ]),
            check_output.call_args_list
        )

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    def test__backup__collection_does_not_exist__command_called(self, check_output, *args):

        m = mongobar.Mongobar()
        m.backup(databases=["d1"], collections=["foobar"])

        self.assertIn(
            mock.call([
                "mongodump",
                "-h", "localhost",
                "-p", "27017",
                "--db", "d1",
                "--collection", "foobar",
                "--out", os.path.join(m.config.connection.directory, "foo-bar"),
                "--quiet",
                "--gzip"
            ]),
            check_output.call_args_list
        )


    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_backup_name", return_value="foo-bar")
    @mock.patch("mongobar.mongobar.get_directories", return_value=[])
    @mock.patch("mongobar.mongobar.create_directory", return_value=True)
    @mock.patch("mongobar.Mongobar.generate_metadata", return_value=MOCKED_BACKUP_METADATA_1_DB)
    @mock.patch("mongobar.Mongobar.write_metadata")
    @mock.patch("mongobar.mongobar.subprocess.check_output", side_effect=[subprocess.CalledProcessError(1, "")])
    def test__backup__collection_arg__raises_CalledProcessError(self, check_output, *args):
        m = mongobar.Mongobar()
        with self.assertRaises(mongobar.exceptions.CommandError):
            m.backup(collections=["foobar"])

    # restore

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    @mock.patch("mongobar.mongobar.os.path.exists", return_value=False)
    def test__restore__raises_BackupNotFoundError(self, *args):
        m = mongobar.Mongobar()
        with self.assertRaises(mongobar.exceptions.BackupNotFoundError):
            m.restore("foobar")

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    @mock.patch("mongobar.mongobar.os.path.exists")
    def test__restore(self, *args):
        m = mongobar.Mongobar()
        m.restore("d1")

        directory = os.path.join(m.config.connection.directory, "d1")

        self.assertIn(
            mock.call([
                "mongorestore",
                "-h", "localhost",
                "-p", "27017",
                "--nsInclude", "d1.*",
                "--drop",
                "--dir", directory,
                "--gzip"
            ]),
            args[1].call_args_list
        )

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    @mock.patch("mongobar.mongobar.os.path.exists")
    def test__restore__databases_arg__raises_DatabaseNotFoundInBackupError(self, *args):
        m = mongobar.Mongobar()
        with self.assertRaises(mongobar.exceptions.DatabaseNotFoundInBackupError):
            m.restore("backup", databases=["foobar"])

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    @mock.patch("mongobar.mongobar.os.path.exists")
    def test__restore__collections_arg__raises_CollectionNotFoundInBackupError(self, *args):
        m = mongobar.Mongobar()
        with self.assertRaises(mongobar.exceptions.CollectionNotFoundInBackupError):
            m.restore("backup", collections=["foobar"])

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    @mock.patch("mongobar.mongobar.os.path.exists")
    def test__restore__destination_databases_arg__raises_DestinationDatabasesLengthError(self, *args):
        m = mongobar.Mongobar()
        with self.assertRaises(mongobar.exceptions.DestinationDatabasesLengthError):
            m.restore("backup", destination_databases=["foobar"])

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    @mock.patch("mongobar.mongobar.os.path.exists")
    def test__restore__authentication_options(self, *args):
        m = mongobar.Mongobar()
        m.config.add({
            "connections": {
                "default": {
                    "host": "localhost",
                    "port": 27017,
                    "username": "user",
                    "password": "pass",
                    "authdb": "authdb"
                }
            }
        })
        m.restore("backup")

        directory = os.path.join(m.config.connection.directory, "backup")

        self.assertIn(
            mock.call([
                "mongorestore",
                "-h", "localhost",
                "-p", "27017",
                "-u", "user",
                "-p", "pass",
                "--authenticationDatabase", "authdb",
                "--nsInclude", "d1.*",
                "--drop",
                "--dir", directory,
                "--gzip"
            ]),
            args[1].call_args_list
        )

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    @mock.patch("mongobar.mongobar.os.path.exists")
    def test__restore__destination_databases_arg(self, *args):
        m = mongobar.Mongobar()
        m.restore("backup", databases=["d1"], destination_databases=["destination"])

        args[1].assert_called_with([
            "mongorestore",
            "-h", "localhost",
            "-p", "27017",
            "--db", "destination",
            "--nsInclude", "d1.*",
            "--drop",
            "--dir", "/root/.mongobar_backups/localhost:27017/backup/d1",
            "--gzip"
        ])

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output", side_effect=[subprocess.CalledProcessError(1, "")])
    @mock.patch("mongobar.mongobar.os.path.exists")
    def test__restore__raises_CommandError(self, *args):
        m = mongobar.Mongobar()
        with self.assertRaises(mongobar.exceptions.CommandError):
            m.restore("backup")

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output")
    @mock.patch("mongobar.mongobar.os.path.exists")
    def test__restore__collection_arg(self, *args):
        m = mongobar.Mongobar()
        m.restore("backup", collections=["c1"])

        self.assertIn(
            mock.call([
                "mongorestore",
                "-h", "localhost",
                "-p", "27017",
                "--nsInclude", "d1.c1",
                "--drop",
                "--dir", os.path.join(m.config.connection.directory, "backup"),
                "--gzip"
            ]),
            args[1].call_args_list
        )

    @mock.patch("mongobar.Mongobar.backup")
    @mock.patch("mongobar.Mongobar.read_metadata", return_value=MOCKED_BACKUP_METADATA_3_DBS)
    @mock.patch("mongobar.mongobar.subprocess.check_output", side_effect=[subprocess.CalledProcessError(1, "")])
    @mock.patch("mongobar.mongobar.os.path.exists")
    def test__restore__collection_arg__raises_CommandError(self, *args):
        m = mongobar.Mongobar()

        with self.assertRaises(mongobar.exceptions.CommandError):
            m.restore("backup", collections=["c1"])

    # list hosts

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=False)
    @mock.patch("mongobar.mongobar.get_directories", return_value=["d1", "d2"])
    def test__get_hosts__directory_does_not_exist(self, *args):
        m = mongobar.Mongobar()
        self.assertEqual(m.get_hosts(), [])

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    @mock.patch("mongobar.mongobar.get_directories", return_value=["d1", "d2"])
    def test__get_hosts__return_names(self, *args):
        m = mongobar.Mongobar()
        m.get_hosts()
        args[0].assert_called_with(m.config.root)

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    @mock.patch("mongobar.mongobar.get_directories", side_effect=[["host"],["db"]])
    def test__get_hosts__return_names_and_counts(self, *args):
        m = mongobar.Mongobar()
        m.get_hosts(count=True)

        self.assertEqual(
            args[0].call_args_list,
            [
                mock.call(m.config.root),
                mock.call(os.path.join(m.config.root, "host"))
            ]
        )

    # list backups

    @mock.patch("mongobar.utils.os.path.exists", return_value=True)
    @mock.patch("mongobar.mongobar.get_directories", return_value=["d1", "d2"])
    def test__get_backups(self, *args):
        m = mongobar.Mongobar()
        m.get_backups()
        args[0].assert_called_with(m.config.connection.directory)

    @mock.patch("mongobar.utils.os.path.exists", return_value=False)
    @mock.patch("mongobar.mongobar.create_directory")
    @mock.patch("mongobar.mongobar.get_directories", return_value=["d1", "d2"])
    def test__get_backups__directory_does_not_exist__return_empty_list(self, *args):
        m = mongobar.Mongobar()
        self.assertEqual(m.get_backups(), [])

    # remove backup

    @mock.patch("mongobar.mongobar.shutil.rmtree")
    @mock.patch("mongobar.mongobar.os.path.exists", return_value=True)
    def test__remove_backup(self, *args):
        m = mongobar.Mongobar()
        m.remove_backup("foo")
        backup_directory = m.config.connection.directory
        args[1].assert_called_with(os.path.join(backup_directory, "foo"))

    @mock.patch("mongobar.mongobar.os.path.exists", return_value=False)
    @mock.patch("mongobar.mongobar.shutil.rmtree")
    def test__remove_backup__raises_BackupNotFoundError(self, *args):
        m = mongobar.Mongobar()
        with self.assertRaises(mongobar.exceptions.BackupNotFoundError):
            m.remove_backup("foo")
