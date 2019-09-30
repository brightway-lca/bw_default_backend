from .filesystem import create_dir, check_dir
from .schema import *
from brightway.peewee import SubstitutableDatabase
import os
import stats_arrays as sa


class Config:
    __brightway_common_api__ = True
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
        'uncertainty type': UncertaintyType,
    }
    directories = [
        'db',
        'processed',
        'output',
    ]

    def __init__(self):
        self.__reset__()

    def __reset__(self):
        self.project = None
        self.database = SubstitutableDatabase(tables=list(self.provides.values()))

    def activate_project(self, project):
        print("Calling activate_project:", project, project.directory)
        self.project = project
        self.database._change_path(project.directory / "db" / "data.db")
        print("Config project:", self.project.directory)

    def deactivate_project(self, project):
        self.project = None
        self.database.close()

    def create_project(self, project):
        if not check_dir(project.directory):
            raise ValueError("Project directory doesn't exist or is not writable")
        for name in self.directories:
            create_dir(project.directory / name)
        self.database._change_path(project.directory / "db" / "data.db")

        # Create basic uncertainty distributions
        for i in range(max(sa.uncertainty_choices.id_dict)):
            try:
                obj = sa.uncertainty_choices.id_dict[i]
                UncertaintyType.create(
                    id=i,
                    label=obj.description
                )
            except KeyError:
                UncertaintyType.create(
                    id=i,
                    label="Dummy uncertainty for missing `stats_arrays` value {}".format(i)
                )

    def copy_project(self, name):
        self.copied = name

    def delete_project(self, name):
        """No-op, as directory will be deleted"""
        pass

    def export_project(self, name):
        self.exported = name

    def import_project(self, name):
        self.imported = name

    @property
    def processed_dir(self):
        if not self.dirpath:
            raise ValueError("Backend has not been activated")
        return os.path.join(self.dirpath, "processed")
