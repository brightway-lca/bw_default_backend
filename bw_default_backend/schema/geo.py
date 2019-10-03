from peewee import TextField, ForeignKeyField, Model
from .generic import DataModel


class Geocollection(DataModel):
    name = TextField(unique=True)


class Location(DataModel):
    geocollection = ForeignKeyField(Geocollection, backref='locations')
    name = TextField()

    class Meta:
        indexes = (
            (('geocollection', 'name'), True),
        )
