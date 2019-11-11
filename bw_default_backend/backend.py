from .filesystem import create_dir, check_dir
from .schema import (
    Activity,
    Collection,
    Exchange,
    Flow,
    Geocollection,
    Location,
    Method,
    CharacterizationFactor,
    UncertaintyType,
    TABLES,
)
from bw_projects.peewee import SubstitutableDatabase
import os
import stats_arrays as sa


class Config:
    __brightway_common_api__ = True
    __brightway_common_api_version__ = 1
    label = "default-backend"
    directories = ["db", "processed", "output"]

    def __init__(self):
        self.__reset__()

    def __reset__(self):
        self.project = None
        self.database = SubstitutableDatabase(tables=TABLES)

    def activate_project(self, project):
        self.project = project
        self.database._change_path(project.directory / "db" / "data.db")

    def deactivate_project(self):
        self.project = None
        self.database.close()

    def create_project(self, project, add_base_data=False, **kwargs):
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
        COLLECTION_TEMPLATE = """CREATE TRIGGER update_collection_modified_{verb}{extra} after {verb}
                on exchange
                begin
                    update collection set modified = current_timestamp where id in (select activity.collection_id from activity where activity.id = {no}.activity_id);
                end;"""
        GENERIC_TEMPLATE = """CREATE TRIGGER update_{table}_modified_{verb}{extra} after {verb}
                on {child}
                begin
                    update {table} set modified = current_timestamp where id = {no}.{table}_id;
                end;"""

        self.database.execute_sql(COLLECTION_TEMPLATE.format(verb="delete", no="OLD", extra=""))
        self.database.execute_sql(COLLECTION_TEMPLATE.format(verb="insert", no="NEW", extra=""))
        self.database.execute_sql(COLLECTION_TEMPLATE.format(verb="update", no="OLD", extra="1"))
        self.database.execute_sql(COLLECTION_TEMPLATE.format(verb="update", no="NEW", extra="2"))
        self.database.execute_sql(GENERIC_TEMPLATE.format(verb="delete", table="method", child="characterizationfactor", no="OLD", extra=""))
        self.database.execute_sql(GENERIC_TEMPLATE.format(verb="insert", table="method", child="characterizationfactor", no="NEW", extra=""))
        self.database.execute_sql(GENERIC_TEMPLATE.format(verb="update", table="method", child="characterizationfactor", no="NEW", extra="1"))
        self.database.execute_sql(GENERIC_TEMPLATE.format(verb="update", table="method", child="characterizationfactor", no="OLD", extra="2"))
        self.database.execute_sql(GENERIC_TEMPLATE.format(verb="delete", table="geocollection", child="location", no="OLD", extra=""))
        self.database.execute_sql(GENERIC_TEMPLATE.format(verb="insert", table="geocollection", child="location", no="NEW", extra=""))
        self.database.execute_sql(GENERIC_TEMPLATE.format(verb="update", table="geocollection", child="location", no="NEW", extra="1"))
        self.database.execute_sql(GENERIC_TEMPLATE.format(verb="update", table="geocollection", child="location", no="OLD", extra="2"))

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
        if not self.project:
            raise ValueError("Backend has not been activated")
        return self.project.directory / "processed"
