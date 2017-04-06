import os
from .peewee import database
from .filesystem import create_dir, check_dir
from .schema import *


class Config:
    implements_common_api = True
    provides = {
        'activity': Activity,
        'characterization factor': CharacterizationFactor,
        'collection': Collection,
        'exchange': Exchange,
        'flow': Flow,
        'geocollection': Geocollection,
        'location': Location,
        'method': Method,
    }
    directories = [
        'db',
        'processed',
        'output',
    ]

    def activate(self, dirpath):
        if not check_dir(dirpath):
            raise ValueError("Provided directory is not valid or writable")
        self.dirpath = dirpath
        for name in self.directories:
            create_dir(os.path.join(self.dirpath, name))
        database.init(os.path.join(self.dirpath, "db", "data.db"))
        database.create_tables(
            list(self.provides.values()),
            safe=True
        )

    @property
    def processed_dir(self):
        if not self.dirpath:
            raise ValueError("Backend has not been activated")
        return os.path.join(self.dirpath, "processed")

    def deactivate(self):
        self.dirpath = None
        database.close()
        database.database = None
