from brightway_projects.peewee import JSONField
from peewee import TextField, Model, fn


class ExtendedModel(Model):
    """Base class for default backend models which adds some basic functionality."""

    @classmethod
    def reformat(cls, dct):
        return dct

    @classmethod
    def span(cls):
        return (
            cls.select(fn.MIN(cls.id)).scalar(),
            cls.select(fn.MAX(cls.id)).scalar(),
        )

    @classmethod
    def max(cls):
        """Get the maximum integer id used in this table.

        Guaranteed to return an integer (i.e. never ``None``)."""
        return cls.select(fn.MAX(cls.id)).scalar() or 0


class DataModel(ExtendedModel):
    """Class that stores extra attributes and values in ``.data``."""

    data = JSONField(default={})

    def __getitem__(self, key):
        if key in self._meta.sorted_field_names:
            return getattr(self, key)
        else:
            return self.data[key]

    def __setitem__(self, key, value):
        if key in self._meta.sorted_field_names:
            setattr(self, key, value)
        else:
            self.data[key] = value

    @classmethod
    def reformat(cls, dct):
        """Reformat a dictionary to put data in correct keys, including ``data``."""
        fn = [x for x in cls._meta.sorted_field_names if x != "data"] + ["id"]
        return {
            "data": {k: v for k, v in dct.items() if k not in fn},
            **{k: v for k, v in dct.items() if k in fn},
        }


class UncertaintyType(ExtendedModel):
    label = TextField()

    def __str__(self):
        return "Uncertainty Type {}".format(self.label)

    def __repr__(self):
        return "Uncertainty Type {}:{}".format(self.id, self.label)
