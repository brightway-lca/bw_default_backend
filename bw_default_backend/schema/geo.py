from brightway.peewee import JSONField
from peewee import TextField, ForeignKeyField, Model


class Geocollection(Model):
    name = TextField(unique=True)
    data = JSONField(default={})


class Location(Model):
    geocollection = ForeignKeyField(Geocollection, backref='locations')
    name = TextField()

    class Meta:
        indexes = (
            (('geocollection', 'name'), True),
        )
