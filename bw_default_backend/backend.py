from .filesystem import create_dir, check_dir
from .schema import (
    Activity,
    Collection,
    collections,
    Exchange,
    Flow,
    Geocollection,
    Location,
    Method,
    CharacterizationFactor,
    UncertaintyType,
)
from brightway_projects.peewee import SubstitutableDatabase
import os
import stats_arrays as sa

TABLES = (
    Activity,
    Collection,
    Exchange,
    Flow,
    Geocollection,
    Location,
    Method,
    CharacterizationFactor,
    UncertaintyType,
)


class Config:
    __brightway_common_api__ = True
    __brightway_common_api_version__ = 1
    label = "default-backend"
    directories = ["db", "processed", "output"]

    def __init__(self):
        self.__reset__()

    def __reset__(self):
        self.project = None
        self.database = SubstitutableDatabase(tables=list(TABLES))

    def activate_project(self, project):
        self.project = project
        self.database._change_path(project.directory / "db" / "data.db")

    def deactivate_project(self, project):
        self.project = None
        self.database.close()

    def create_project(self, project, add_base_data=True):
        if not check_dir(project.directory):
            raise ValueError("Project directory doesn't exist or is not writable")
        for name in self.directories:
            create_dir(project.directory / name)
        self.database._change_path(project.directory / "db" / "data.db")

        self.__create_triggers()

        if add_base_data:
            # Create basic uncertainty distributions
            for i in range(max(sa.uncertainty_choices.id_dict)):
                try:
                    obj = sa.uncertainty_choices.id_dict[i]
                    UncertaintyType.create(id=i, label=obj.description)
                except KeyError:
                    UncertaintyType.create(
                        id=i,
                        label="Dummy uncertainty for missing `stats_arrays` value {}".format(
                            i
                        ),
                    )

            world = Geocollection.create(name="world")
            Location.create(geocollection=world, name="Global")

    def __create_triggers(self):
        self.database.execute_sql(
            """CREATE TRIGGER update_collection_modified_delete after delete
                on exchange
                begin
                    update collection set modified = current_timestamp where id in (select distinct activity.collection_id from activity join exchange on activity.id = exchange.activity_id);
                end;"""
        )
        self.database.execute_sql(
            """CREATE TRIGGER update_collection_modified_insert after insert
                on exchange
                begin
                    update collection set modified = current_timestamp where id in (select distinct activity.collection_id from activity join exchange on activity.id = exchange.activity_id);
                end;"""
        )
        self.database.execute_sql(
            """CREATE TRIGGER update_collection_modified_update after update
                on exchange
                begin
                    update collection set modified = current_timestamp where id in (select distinct activity.collection_id from activity join exchange on activity.id = exchange.activity_id);
                end;"""
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
