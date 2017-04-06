class WrongDatabase(Exception):
    """Peewee object is not from the same database as the current config"""
    pass
