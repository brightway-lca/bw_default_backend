import os
from .peewee import database
from .filesystem import create_dir, check_dir
from .schema import *


class Config:
    implements_common_api = True
    label = "default-backend"
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
        self.dirpath = Path(dirpath)
        if not self.dirpath.is_dir():
            raise ValueError("provided `dirpath` does not exist")
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
