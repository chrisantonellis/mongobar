import os
import sys
import logging
import pkgutil
import random
import pymongo
import datetime
import copy
import json
import subprocess
import shutil

from mongobar.utils import create_directory
from mongobar.utils import get_directories

from mongobar.config import Config

from mongobar.exceptions import ServerConnectionError
from mongobar.exceptions import CommandError
from mongobar.exceptions import BackupNotFoundError
from mongobar.exceptions import DatabaseNotFoundInBackupError
from mongobar.exceptions import CollectionNotFoundInBackupError
from mongobar.exceptions import DestinationDatabasesLengthError


class Mongobar(object):

    def __init__(self):
        self.logger = logging.getLogger("mongobar")
        self.config = Config()

    def generate_backup_name(self):

        # TODO: try, catch for potential get_data errors like returning None
        # https://docs.python.org/2/library/pkgutil.html#pkgutil.get_data

        verbs_bytes = pkgutil.get_data("mongobar", "data/verbs.txt")
        verbs = verbs_bytes.decode("utf-8").split("\n")
        verb = random.choice(verbs)

        # get random noun
        nouns_bytes = pkgutil.get_data("mongobar", "data/nouns.txt")
        nouns = nouns_bytes.decode("utf-8").split("\n")
        noun = random.choice(nouns)

        return "{}-{}".format(verb, noun)

    def create_pymongo_client(self):

        connection = self.config.connection

        options = {
            "host": connection.host,
            "port": connection.port
        }

        if connection.auth:
            options["username"] = connection.username
            options["password"] = connection.password
            if connection.authdb is not None:
                options["authSource"] = connection.authdb

        try:
            client = pymongo.MongoClient(**options)

            # test connection
            client.database_names()

            return client

        except pymongo.errors.PyMongoError as e:
            raise ServerConnectionError(e)

    def generate_metadata(self, databases=None, collections=None):

        connection = self.config.connection
        client = self.create_pymongo_client()

        metadata = {
            "host": connection.host,
            "port": connection.port,
            "date": datetime.datetime.today().isoformat(),
            "databases": []
        }

        dbs = databases or client.database_names()
        if "local" in dbs:
            dbs.remove("local")

        for db in dbs:
            db_metadata = {
                "name": db,
                "collections": []
            }

            for collection in collections or client[db].collection_names():
                db_metadata["collections"].append({
                    "name": collection,
                    "document_count": client[db][collection].count()
                })

            if db_metadata["collections"]:
                metadata["databases"].append(db_metadata)

        client.close()

        return metadata

    def write_metadata(self, name, data):

        metadata_path = os.path.join(
            self.config.connection_dir,
            name,
            "metadata.json"
        )

        with open(metadata_path, "w+") as file_handle:
            json.dump(data, file_handle)

        return True

    def read_metadata(self, name):

        connection = self.config.connection

        metadata_path = os.path.join(
            self.config.connection_dir,
            name,
            "metadata.json"
        )

        try:
            with open(metadata_path, "r") as file_handle:
                metadata = json.loads(file_handle.read())

        except FileNotFoundError:
            metadata = {
                "host": connection.host,
                "port": connection.port,
                "date": "0001-01-01T00:00:00.0000",
                "databases": [],
                "message": "Metadata not found"
            }

        return metadata

    def backup(self, message=None, databases=None, collections=None):

        # create root directory if necessary
        root_dir = self.config.root
        if not os.path.exists(root_dir):
            self.logger.debug("Root directory '{}' created".format(root_dir))
            create_directory(root_dir)

        # create backup directory if necessary
        conn_dir = self.config.connection_dir
        if not os.path.exists(conn_dir):
            self.logger.debug("Backup directory '{}' created".format(conn_dir))
            create_directory(conn_dir)

        # generate unique backup name
        while 1:
            backup_name = self.generate_backup_name()
            if backup_name not in get_directories(conn_dir):
                break

        # create backup directory
        backup_dir = os.path.join(conn_dir, backup_name)
        create_directory(backup_dir)

        # pymongo client
        client = self.create_pymongo_client()

        # determine dbs
        all_databases = client.database_names()
        dbs = databases or all_databases
        if "local" in dbs:
            dbs.remove("local")

        # generate metadata
        metadata = self.generate_metadata(dbs, collections)
        metadata["name"] = backup_name
        metadata["message"] = message
        self.write_metadata(backup_dir, metadata)

        # get connection
        conn = self.config.connection

        for db in dbs:

            if db not in all_databases:
                msg = "Database '{}' does not exist"
                msg = msg.format(db)
                self.logger.warning(msg)

            command = ["mongodump"]
            command += ["--host", conn.host]
            command += ["--port", str(conn.port)]

            if conn.auth:
                command += ["-u", conn.username]
                command += ["-p", conn.password]
                if conn.authdb is not None:
                    command += ["--authenticationDatabase", conn.authdb]

            command += ["--db", db]

            command_end = ["--out", backup_dir]
            command_end += ["--quiet"]
            command_end += ["--gzip"]

            # call command once per datbase
            if not collections:
                command += command_end

                try:
                    subprocess.check_output(command)
                    self.logger.debug("Command called: {}".format(" ".join(command)))
                except subprocess.CalledProcessError as e:
                    raise CommandError(e)

            # call command once per collection
            else:
                all_collections = client[db].collection_names()

                for col in collections:

                    if col not in all_collections:
                        msg = "Collection '{}' does not exist in database '{}'"
                        msg = msg.format(col, db)
                        self.logger.warning(msg)

                    col_command = copy.copy(command)
                    col_command += ["--collection", col]
                    col_command += command_end

                    try:
                        subprocess.check_output(col_command)
                        self.logger.debug("Command called: {}".format(" ".join(col_command)))
                    except subprocess.CalledProcessError as e:
                        raise CommandError(e)

        return backup_name

    def restore(self, name, databases=None, collections=None, \
            destination_databases=None, destination_connection=None):

        # check if backup directory exists
        backup_dir = os.path.join(self.config.connection_dir, name)
        if not os.path.exists(backup_dir):
            raise BackupNotFoundError(name)

        # read backup metadata
        metadata = self.read_metadata(name)

        # check databases against metadata
        if databases:
            for database in databases:
                if database not in [d["name"] for d in metadata["databases"]]:
                    raise DatabaseNotFoundInBackupError(database, name)

        # check collections against metadata
        if collections:
            for database in metadata["databases"]:
                for collection in collections:
                    if collection not in [c["name"] for c in database["collections"]]:
                        raise CollectionNotFoundInBackupError(database, collection, name)

        # check destination databases against databases
        if destination_databases:
            databases_len = len(databases or metadata["databases"])
            destination_databases_len = len(destination_databases)
            if databases_len != destination_databases_len:
                raise DestinationDatabasesLengthError(
                    databases_len,
                    destination_databases_len
                )

        conn = self.config.connection
        dest_conn = self.config.connections.get(destination_connection or self.config.connection.name)

        # iterate databases and collections
        for i, database in enumerate(databases or [d["name"] for d in metadata["databases"]]):

            # command, host and port
            command = ["mongorestore"]
            command += ["--host", dest_conn.host]
            command += ["--port", str(dest_conn.port)]

            # authentication
            if dest_conn.auth:
                command += ["-u", dest_conn.username]
                command += ["-p", dest_conn.password]

                if dest_conn.authdb is not None:
                    command += ["--authenticationDatabase", dest_conn.authdb]

            # destination databases
            if destination_databases:
                command += ["--db", destination_databases[i]]

            # command output
            command_out = ["--drop"]
            source_dir = copy.copy(backup_dir)
            if destination_databases:
                source_dir = os.path.join(source_dir, database)
            command_out += ["--dir", source_dir]
            command_out += ["--gzip"]

            if not collections:

                command += ["--nsInclude", "{}.*".format(database)]
                command += command_out

                try:
                    self.logger.debug("Command called: {}".format(" ".join(command)))
                    subprocess.check_output(command)
                except subprocess.CalledProcessError as e:
                    raise CommandError(e)

            else:

                for collection in collections:

                    collection_command = copy.copy(command)
                    collection_command += ["--nsInclude", "{}.{}".format(database, collection)]
                    collection_command += command_out

                    try:
                        self.logger.debug("Command called: {}".format(" ".join(collection_command)))
                        subprocess.check_output(collection_command)
                    except subprocess.CalledProcessError as e:
                        raise CommandError(e)

    def get_connection_directories(self, count=False):
        if not os.path.exists(self.config.root):
            return []

        directories = []
        for directory in get_directories(self.config.root):

            if count:
                path = os.path.join(self.config.root, directory)
                backup_count = len(get_directories(path))
                directories.append((directory, backup_count))

            else:
                directories.append(directory)

        return directories

    def get_backups(self):
        path = self.config.connection_dir

        if not os.path.exists(path):
            return []

        return get_directories(path)

    def remove_backup(self, name):
        path = os.path.join(self.config.connection_dir, name)

        if not os.path.exists(path):
            raise BackupNotFoundError(name)

        shutil.rmtree(path)
