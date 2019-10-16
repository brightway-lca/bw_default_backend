from .geo import Geocollection
from .lci import Collection
from .lcia import Method
from peewee import ForeignKeyField, DateTimeField, Model, SQL
from brightway_projects.peewee import PathField


class CalculationPackage(Model):
    filepath = PathField()
    modified = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    geocollection = ForeignKeyField(Geocollection, null=True)
    collection = ForeignKeyField(Collection, null=True)
    method = ForeignKeyField(Method, null=True)
