from . import Flow
from .generic import DataModel, UncertaintyType

from bw_projects.peewee import TupleField
from peewee import ForeignKeyField, DateTimeField, FloatField, SQL, DoesNotExist
import datetime


class Method(DataModel):
    name = TupleField(unique=True)
    modified = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])

    def __str__(self):
        return "Method {}".format(self.name)

    def __repr__(self):
        return "Method {}:{} ({})".format(self.id, self.name, self.modified)

    @property
    def package(self):
        from . import CalculationPackage
        try:
            cp = CalculationPackage.get(method = self)
            if self.modified > cp.modified:
                self.process()
        except DoesNotExist:
            self.process()
        return CalculationPackage.get(collection = self).filepath

    def process(self, **kwargs):
        from .. import Processor
        processor = Processor({'method': [self]})
        processor.gather_data()
        return processor.write_package(**kwargs)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        super().save(*args, **kwargs)


class CharacterizationFactor(DataModel):
    flow = ForeignKeyField(Flow, backref="cfs")
    method = ForeignKeyField(Method, backref="cfs")
    amount = FloatField()
    uncertainty_type = ForeignKeyField(UncertaintyType, null=True, backref="cfs")

    def __repr__(self):
        return "Characterization Factor {} {} ({})".format(
            self.amount, self.flow, self.method
        )
