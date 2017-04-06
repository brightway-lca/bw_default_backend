from . import ProjectAwareModel
from ..peewee import database, JSONField
from peewee import TextField, ForeignKeyField


class Geocollection(ProjectAwareModel):
    name = TextField(unique=True)
    data = JSONField()


class Location(ProjectAwareModel):
    geocollection = ForeignKeyField(Geocollection, related_name='locations')
    name = TextField()

    class Meta:
        database = database
        indexes = (
            (('geocollection', 'name'), True),
        )
