from peewee import TextField, ForeignKeyField, Model
from .generic import DataModel


class Geocollection(DataModel):
    name = TextField(unique=True)

    def __str__(self):
        return "Geocollection {}".format(self.name)

    def __repr__(self):
        return "Geocollection {}:{}".format(self.id, self.name)


class Location(DataModel):
    geocollection = ForeignKeyField(Geocollection, backref='locations')
    name = TextField()

    def __str__(self):
        return "Location {}".format(self.name)

    def __repr__(self):
        return "Location {}:{} ({})".format(self.id, self.name, self.geocollection)

    class Meta:
        indexes = (
            (('geocollection', 'name'), True),
        )
