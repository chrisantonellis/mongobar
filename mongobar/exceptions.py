
class BaseError(Exception):
    msg = ""

    def __init__(self, *args):
        msg = self.msg.format(*args) if args else self.msg
        super().__init__(msg)


class ServerConnectionError(BaseError):
    msg = "Connection error: {}"


class ConnectionNotSetError(BaseError):
    msg = "Connection '{}' not set"


class ConnectionAttributeNotSetError(BaseError):
    msg = "Connection attribute '{}' not set"


class BackupNotFoundError(BaseError):
    msg = "Backup '{}' not found"


class CommandError(BaseError):
    msg = "Command failed: {}"


class DatabaseNotFoundInBackupError(BaseError):
    msg = "Database '{}' not found in backup '{}'"


class CollectionNotFoundInBackupError(BaseError):
    msg = "Collection '{}' not found in database '{}' in backup '{}'"


class DestinationDatabasesLengthError(BaseError):
    msg = "Number of databases ({}) and destination databases ({}) must match."
