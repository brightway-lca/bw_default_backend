from brightway_projects.filesystem import safe_filename
from brightway_projects.peewee import JSONField, TupleField
from .geo import Location
from .generic import UncertaintyType
from peewee import TextField, ForeignKeyField, DateTimeField, FloatField, fn, Model
import datetime
import os


class Collection(Model):
    name = TextField(unique=True)
    data = JSONField(default={})
    dependents = JSONField(null=True)
    modified = DateTimeField(default=datetime.datetime.now)

    def random(self):
        """Get a random `Activity`"""
        return self.activities.order_by(fn.Random()).get()

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        super().save(*args, **kwargs)

    def dependents(self):
        """Find the `Collections` that are consumed by `Activities` in this `Collection`."""
        consumed_flows = Exchange.select(fn.Distinct(Exchange.flow)).where(Exchange.kind == 'technosphere')
        producing_collections = Exchange.join(Activity).select(
            fn.Distinct(Activity.collection)).where(
            Exchange.flow << consumed_flows &
            Exchange.kind == 'production')
        return producing_collections

    def recursive_dependents(self):
        """Get names of all collections consumed by the complete supply chain of this ``Collection``"""
        queue, seen = [obj.name for obj in self.dependents], set([self.name])
        while queue:
            name = queue.pop()
            if name in seen:
                continue
            else:
                seen.add(name)
                queue.extend([
                    obj.name for obj in Collection(name).dependents()
                    if obj.name not in seen
                ])
        return seen

    @property
    def filepath_geoarray(self):
        from .. import config
        return os.path.join(
            config.processed_dir,
            "geoarray." + safe_filename(self.name)
        )

    @property
    def filepath_technosphere(self):
        from .. import config
        return os.path.join(
            config.processed_dir,
            "technosphere." + safe_filename(self.name)
        )

    @property
    def filepath_biosphere(self):
        from .. import config
        return os.path.join(
            config.processed_dir,
            "biosphere." + safe_filename(self.name)
        )


class CollectionList:
    def __contains__(self, name):
        return bool(Collection.select().where(Collection.name == name).count())

    def __iter__(self):
        return Collection.select().order_by(Collection.name)

    def __len__(self):
        return Collection.select().count()


collections = CollectionList()


class Flow(Model):
    name = TextField()
    unit = TextField()
    kind = TextField()
    location = ForeignKeyField(Location, null=True, backref='flows')
    collection = ForeignKeyField(Collection, backref='flows')
    categories = TupleField(default=[])
    data = JSONField(default={})


class Activity(Model):
    name = TextField()
    unit = TextField(null=True)
    collection = ForeignKeyField(Collection, backref='activities')
    location = ForeignKeyField(Location, null=True, backref='activities')
    reference_product = ForeignKeyField(Flow, null=True)
    data = JSONField(default={})

    def __getitem__(self, key):
        if key in ("name", "unit", "collection", "location", "reference_product"):
            return getattr(self, key)
        else:
            return self.data[key]

    def technosphere(self):
        return self.exchanges.where(kind == 'technosphere')

    def biosphere(self):
        return self.exchanges.where(kind == 'biosphere')

    def production(self):
        return self.exchanges.where(kind == 'production')

    def consumers(self):
        return Exchange.select().where(
            kind == 'technosphere' &
            flow << self.exchanges.select(Exchange.flow).where(
                Exchange.kind == 'production'
            )
        )


class Exchange(Model):
    activity = ForeignKeyField(Activity, backref='exchanges')
    flow = ForeignKeyField(Flow, backref='exchanges')
    direction = TextField(default="consumption")
    data = JSONField(default={})
    amount = FloatField()
    uncertainty_type = ForeignKeyField(UncertaintyType, null=True, backref='exchanges')

    # def save(self):
    #     if self.uncertainty_type is not None:
    #         uncertainty_choices[self.uncertainty_type.id].validate(self.data)
    #     super().save()
