class BrightwayDefaultBackendError(Exception):
    pass


class WrongDatabase(BrightwayDefaultBackendError):
    """Peewee object is not from the same database as the current config"""

    pass


class MissingFlow(BrightwayDefaultBackendError):
    """Given Flow is not present in this database"""

    pass


class Duplicate(BrightwayDefaultBackendError):
    """Attempted duplicate creation of a unique object"""

    pass


class MissingObject(BrightwayDefaultBackendError):
    """Object referenced in input data does not exist in database"""

    pass


class NoActiveProject(BrightwayDefaultBackendError):
    """Operation requires a project, but no project is active"""

    pass
