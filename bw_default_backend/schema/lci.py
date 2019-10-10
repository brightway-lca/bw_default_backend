from .generic import UncertaintyType, DataModel
from .geo import Location
from brightway_projects.filesystem import safe_filename
from brightway_projects.peewee import TupleField
from peewee import TextField, ForeignKeyField, DateTimeField, FloatField, fn, SQL
import datetime


class Collection(DataModel):
    name = TextField(unique=True)
    modified = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    def __str__(self):
        return "Collection {}".format(self.name)

    def __repr__(self):
        return "Collection {}:{} ({})".format(self.id, self.name, self.modified)

    def random_activity(self):
        """Get a random `Activity`"""
        return self.activities.order_by(fn.Random()).get()

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        super().save(*args, **kwargs)

    def dependents(self):
        """Find the `Collections` that are consumed by `Activities` in this `Collection`."""
        qs = (
            Exchange.select(fn.Distinct(Flow.collection_id))
            .join(Flow, on=(Exchange.flow_id == Flow.id))
            .join(Activity, on=(Exchange.activity_id == Activity.id))
            .where(Activity.collection_id == self.id)
            .tuples()
        )
        ids = [i for i in qs if i != self.id]
        return Collection.select().where(Collection.id << ids)

    def recursive_dependents(self):
        """Get names of all collections consumed by the complete supply chain of this ``Collection``"""
        queue, seen = [obj.name for obj in self.dependents()], set([self.name])
        while queue:
            name = queue.pop()
            if name in seen:
                continue
            else:
                seen.add(name)
                queue.extend(
                    [
                        obj.name
                        for obj in Collection(name).dependents()
                        if obj.name not in seen
                    ]
                )
        return seen

    # @property
    # def filepath_geoarray(self):
    #     from .. import config

    #     return os.path.join(
    #         config.processed_dir, "geoarray." + safe_filename(self.name)
    #     )

    # @property
    # def filepath_technosphere(self):
    #     from .. import config

    #     return os.path.join(
    #         config.processed_dir, "technosphere." + safe_filename(self.name)
    #     )

    # @property
    # def filepath_biosphere(self):
    #     from .. import config

    #     return os.path.join(
    #         config.processed_dir, "biosphere." + safe_filename(self.name)
    #     )


class CollectionList:
    def __contains__(self, name):
        return bool(Collection.select().where(Collection.name == name).count())

    def __iter__(self):
        return Collection.select().order_by(Collection.name)

    def __len__(self):
        return Collection.select().count()


collections = CollectionList()


class Flow(DataModel):
    name = TextField()
    unit = TextField()
    kind = TextField()
    location = ForeignKeyField(Location, null=True, backref="flows")
    collection = ForeignKeyField(Collection, backref="flows")
    categories = TupleField(default=[])

    def __str__(self):
        return "Flow {}".format(self.name)

    def __repr__(self):
        return "Flow {} ({}; {}; {}; {})".format(
            self.name, self.collection, self.location, self.categories, self.unit
        )


class Activity(DataModel):
    name = TextField()
    collection = ForeignKeyField(Collection, backref="activities")
    location = ForeignKeyField(Location, null=True, backref="activities")
    reference_product = ForeignKeyField(Flow, null=True)

    def __str__(self):
        return "Activity {}".format(self.name)

    def __repr__(self):
        return "Activity {} ({}; {}; {}; {})".format(
            self.name, self.collection, self.location, self.reference_product, self.unit
        )

    def technosphere(self):
        return self.exchanges.where(kind == "technosphere")

    def biosphere(self):
        return self.exchanges.where(kind == "biosphere")

    def production(self):
        return self.exchanges.where(kind == "production")

    def consumers(self):
        return Exchange.select().where(
            kind
            == "technosphere"
            & flow
            << self.exchanges.select(Exchange.flow).where(Exchange.kind == "production")
        )


class Exchange(DataModel):
    activity = ForeignKeyField(Activity, backref="exchanges")
    flow = ForeignKeyField(Flow, backref="exchanges")
    direction = TextField(default="consumption")
    amount = FloatField()
    uncertainty_type = ForeignKeyField(UncertaintyType, null=True, backref="exchanges")

    # def save(self):
    #     if self.uncertainty_type is not None:
    #         uncertainty_choices[self.uncertainty_type.id].validate(self.data)
    #     super().save()
