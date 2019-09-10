import os
from brightway.peewee import SubstitutableDatabase
from .schema import TABLES


class Config:
    __brightway_common_api__ = True
    label = "default-backend"

    directories = [
        'db',
        'processed',
        'output',
    ]

    @property
    def processed_dir(self):
        if not self.dirpath:
            raise ValueError
        return self.dirpath / "processed"

    def activate_project(self, obj):
        self.dirpath = obj.directory
        self.db = SubstitutableDatabase(
            self.dirpath / "db" / "data.db",
            TABLES
        )

    def deactivate_project(self, obj):
        self.db.close()
        self.dirpath = None

    def create_project(self, obj):
        self.dirpath = obj.directory
        if not os.access(self.dirpath, os.W_OK):
            raise ValueError("Project directory not writable")
        if not self.dirpath.is_dir():
            raise ValueError("provided `dirpath` does not exist")
        for name in self.directories:
            (self.dirpath / name).mkdir(parents=True, exist_ok=True)

    def copy_project(self, old, new):
        pass
        # self.copied_old = old
        # self.copied_new = new

    def delete_project(self, obj):
        pass
        # self.deleted = obj

    def export_project(self, obj, filepath):
        pass
        # self.exported = obj
        # self.exported_filepath = filepath

    def import_project(self, obj, filepath):
        pass
        # self.imported = obj
        # self.imported_filepath = filepath
