import numpy as np
from bw_processing import (
    create_calculation_package,
    format_calculation_resource,
    MAX_SIGNED_32BIT_INT,
)
from .schema import Exchange, CharacterizationFactor
from .filesystem import safe_filename
from . import config


def filepath_for_processed_array(collection, matrix):
    return config.processed_dir / ("{}.{}.npy".format(safe_filename(collection), matrix))


class Processor:
    """Class to generate structured arrays from one or more collection-type objects."""
    technosphere_kinds = ("production", "technosphere", "substitution")

    def __init__(self, request):
        self.request = request
        self.resources = []

    def gather_data(self):
        if self.request.get("collection"):
            self.process_technosphere()
            self.process_biosphere()
        if self.request.get("method"):
            self.process_method()

    def write_package(self, name, **kwargs):
        return create_calculation_package(name, self.resources, **kwargs)

    # TODO: Skip this for now, as SQLite will
    # convert to 0 so they don't mess up anything.
    def check_value(self, value):
        return not (np.isnan(value) or np.isinf(value))

    @classmethod
    def formatter(cls, row):
        return (
            row["flow_id"],
            row.get("activity_id", row["flow_id"]),
            MAX_SIGNED_32BIT_INT,
            MAX_SIGNED_32BIT_INT,
            row["uncertainty_type_id"],
            row["amount"],
            row["data"].get("loc", row["amount"]),
            row["data"].get("scale", np.NaN),
            row["data"].get("shape", np.NaN),
            row["data"].get("minimum", np.NaN),
            row["data"].get("maximum", np.NaN),
            row["data"].get("negative", False),
            row.get("direction") == "consumption",
        )

    def process_technosphere(self):
        for collection in self.request["collection"]:
            qs = Exchange.select().where(
                Exchange.activity << collection.activities & Exchange.kind << self.technosphere_kinds
            )
            self.resources.append(
                format_calculation_resource(
                    {
                        "name": "f{collection}-technosphere",
                        "matrix": "technosphere",
                        "nrows": qs.count(),
                        "data": qs.order_by(Exchange.id).dicts(),
                        "format_function": self.formatter,
                    }
                )
            )

    def process_biosphere(self):
        for collection in self.request["collection"]:
            qs = Exchange.select().where(
                Exchange.activity << collection.activities & Exchange.kind.not_in(self.technosphere_kinds)
            )
            self.resources.append(
                format_calculation_resource(
                    {
                        "name": "f{collection}-biosphere",
                        "matrix": "technosphere",
                        "nrows": qs.count(),
                        "data": qs.order_by(Exchange.id).dicts(),
                        "format_function": self.formatter,
                    }
                )
            )

    def process_method(self):
        for method in self.request["method"]:
            qs = CharacterizationFactor.select().where(
                CharacterizationFactor.method == method)
            self.resources.append(
                format_calculation_resource(
                    {
                        "name": "f{method}",
                        "matrix": "characterization",
                        "nrows": qs.count(),
                        "data": qs.order_by(CharacterizationFactor.id).dicts(),
                        "format_function": self.formatter,
                    }
                )
            )
