from . import Location, Flow, ProjectAwareModel
from ..peewee import JSONField, TupleField
from ..filesystem import abbreviate
from peewee import TextField, ForeignKeyField, DateTimeField, FloatField
import datetime


class Method(ProjectAwareModel):
    name = TupleField(unique=True)
    data = JSONField()
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


class CharacterizationFactor(ProjectAwareModel):
    flow = ForeignKeyField(Flow, related_name="cfs")
    method = ForeignKeyField(Method, related_name="cfs")
    amount = FloatField()
    uncertainty = JSONField()
    location = ForeignKeyField(Location, null=True)

    def save(self):
        if 'uncertainty type' not in self.uncertainty:
            self.uncertainty['uncertainty type'] = 0
        uncertainty_choices[self['uncertainty']['uncertainty type']].validate(
            self['uncertainty'])
        super().save()
