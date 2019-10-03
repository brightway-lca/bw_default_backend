from . import Location, Flow
from .generic import DataModel
from ..filesystem import abbreviate
from brightway_projects.peewee import JSONField, TupleField
from peewee import TextField, ForeignKeyField, DateTimeField, FloatField, Model
import datetime


class Method(DataModel):
    name = TupleField(unique=True)
    modified = DateTimeField()

    @property
    def filepath_processed(self):
        from .. import config
        return os.path.join(
            config.processed_dir,
            "method." + abbreviate(self.name)
        )

    def save(self):
        self.modified = datetime.datetime.now()
        super().save()


class CharacterizationFactor(DataModel):
    flow = ForeignKeyField(Flow, backref="cfs")
    method = ForeignKeyField(Method, backref="cfs")
    amount = FloatField()
    uncertainty = JSONField()
    location = ForeignKeyField(Location, null=True)

    def save(self):
        if 'uncertainty type' not in self.uncertainty:
            self.uncertainty['uncertainty type'] = 0
        uncertainty_choices[self['uncertainty']['uncertainty type']].validate(
            self['uncertainty'])
        super().save()
