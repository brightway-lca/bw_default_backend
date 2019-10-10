import numpy as np
from brightway_projects.processing import (
    create_numpy_structured_array,
    create_datapackage_metadata,
    format_datapackage_resource,
)
from .schema import Activity, Exchange, Flow


def process_collection(collection):
    process_collection_technosphere(collection)
    process_collection_biosphere(collection)


def get_array(collection, kinds):
    dtype = [
        ("input", np.uint32),
        ("output", np.uint32),
        ("row", np.uint32),
        ("col", np.uint32),
        ("type", np.uint8),
    ] + BASE_UNCERTAINTY_FIELDS

    qs = Exchange.select().where(
        Exchange.activity << collection.activities & Exchange.kind << kinds
    )
    count = qs.count()
    arr = np.zeros((count,), dtype=dtype)

    for index, exc in enumerate(qs.order_by(Exchange.id).dicts()):
        if np.isnan(exc["amount"]) or np.isinf(exc["amount"]):
            raise ValueError("Invalid amount in exchange {}".format(data))

        if exc.get("type") == "technosphere":
            # Input exchanges are consumed, and should be negative
            exc = flip_technosphere_input_exchange(exc)

        arr[index] = (
            exc["flow"],
            exc["activity"],
            MAX_INT_32,
            MAX_INT_32,
            TYPE_DICTIONARY.get(exc["kind"], -1),
            exc["uncertainty"]["uncertainty type"],
            exc["amount"],
            exc["amount"]
            if exc["uncertainty"]["uncertainty type"] in (0, 1)
            else exc["uncertainty"].get("loc", np.NaN),
            exc["uncertainty"].get("scale", np.NaN),
            exc["uncertainty"].get("shape", np.NaN),
            exc["uncertainty"].get("minimum", np.NaN),
            exc["uncertainty"].get("maximum", np.NaN),
            exc["amount"] < 0,
        )

    # Drop unknown exchange types
    return arr[arr["type"] != -1]


def process_collection_technosphere(collection):

    arr = get_array(collection, ("production", "technosphere", "substitution"))
    np.save(collection.filepath_technosphere, arr, allow_pickle=False)
    return collection.filepath_technosphere


def process_collection_biosphere(collection):
    arr = get_array(collection, ("biosphere",))
    np.save(collection.filepath_biosphere, arr, allow_pickle=False)
    return collection.filepath_biosphere


def process_method(method):
    dtype = [
        ("input", np.uint32),
        ("output", np.uint32),
        ("row", np.uint32),
        ("col", np.uint32),
        ("type", np.uint8),
    ] + BASE_UNCERTAINTY_FIELDS

    qs = Exchange.select().where(
        Exchange.activity << collection.activities & Exchange.kind << kinds
    )
    count = qs.count()
    arr = np.zeros((count,), dtype=dtype)

    for index, exc in enumerate(qs.order_by(Exchange.id).dicts()):
        if np.isnan(exc["amount"]) or np.isinf(exc["amount"]):
            raise ValueError("Invalid amount in exchange {}".format(data))

        if exc.get("type") == "technosphere":
            # Input exchanges are consumed, and should be negative
            exc = flip_technosphere_input_exchange(exc)

        arr[index] = (
            exc["flow"],
            exc["activity"],
            MAX_INT_32,
            MAX_INT_32,
            TYPE_DICTIONARY.get(exc["kind"], -1),
            exc["uncertainty"]["uncertainty type"],
            exc["amount"],
            exc["amount"]
            if exc["uncertainty"]["uncertainty type"] in (0, 1)
            else exc["uncertainty"].get("loc", np.NaN),
            exc["uncertainty"].get("scale", np.NaN),
            exc["uncertainty"].get("shape", np.NaN),
            exc["uncertainty"].get("minimum", np.NaN),
            exc["uncertainty"].get("maximum", np.NaN),
            exc["amount"] < 0,
        )

    # Drop unknown exchange types
    return arr[arr["type"] != -1]


def flip_technosphere_input_exchange(exc):
    """Flip sign of exchange dictionary."""
    # No or unknown uncertainty
    if exc["uncertainty"]["uncertainty type"] in (0, 1):
        exc["amount"] *= -1
    # Asymmetric distributions
    if exc["uncertainty"]["uncertainty type"] in (2, 8, 9, 10):
        # TODO: Negative Beta not supported in stats_arrays
        exc["amount"] *= -1
    # Normal, extreme value, and Student's T distributions
    if exc["uncertainty"]["uncertainty type"] in (3, 11, 12):
        exc["amount"] *= -1
        exc["loc"] *= -1
    # Uniform and discrete uniform
    if exc["uncertainty"]["uncertainty type"] in (4, 7):
        exc["amount"] *= -1
        exc["minimum"], exc["maximum"] = (-1 * exc["maximum"], -1 * exc["minimum"])
    # Triangular
    if exc["uncertainty"]["uncertainty type"] == 5:
        exc["amount"] *= -1
        exc["loc"] *= -1
        exc["minimum"], exc["maximum"] = (-1 * exc["maximum"], -1 * exc["minimum"])
    # Bernoulli
    if exc["uncertainty"]["uncertainty type"] == 6:
        # TODO
        exc["amount"] *= -1
