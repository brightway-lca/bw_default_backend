# from .geo import Geocollection
from .lci import Collection
from .lcia import Method
from brightway_projects.filesystem import md5
from brightway_projects.peewee import PathField
from peewee import ForeignKeyField, DateTimeField, Model, SQL, TextField


class CalculationPackage(Model):
    filepath = PathField()
    hash = TextField()
    modified = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    # geocollection = ForeignKeyField(Geocollection, null=True)
    collection = ForeignKeyField(Collection, null=True)
    method = ForeignKeyField(Method, null=True)

    def save(self, *args, **kwargs):
        self.hash = md5(self.filepath)
        super().save(*args, **kwargs)

    class Meta:
        indexes = (
            (("collection_id", "method_id"), True),
        )
