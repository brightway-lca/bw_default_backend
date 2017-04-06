import numpy as np
from .schema import Activity, Exchange, Flow


MAX_INT_32 = 4294967295

# Type of technosphere/biosphere exchanges used in processed Databases
TYPE_DICTIONARY = {
    "production": 0,
    "technosphere": 1,
    "biosphere": 2,
    "substitution": 3,
}

BASE_UNCERTAINTY_FIELDS = [
    ('uncertainty_type', np.uint8),
    ('amount', np.float32),
    ('loc', np.float32),
    ('scale', np.float32),
    ('shape', np.float32),
    ('minimum', np.float32),
    ('maximum', np.float32),
    ('negative', np.bool),
]


def process_collection(collection):
    process_collection_geoarray(collection)
    process_collection_technosphere(collection)
    process_collection_biosphere(collection)


def process_collection_geoarray(collection):
    dtype = [
        ('activity', np.uint32),
        ('geo', np.uint32),
        ('row', np.uint32),
        ('col', np.uint32),
    ] + BASE_UNCERTAINTY_FIELDS

    count = collection.activities.count()
    arr = np.zeros((count,), dtype=dtype)

    for index, data in enumerate(collection.activities.select(
            Activity.id, Activity.location).order_by(Activity.id).tuples()):
        arr[index] = (
            data[0], data[1], MAX_INT_32, MAX_INT_32,
            0, 1, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, False
        )

    np.save(collection.filepath_geoarray, arr, allow_pickle=False)
    return collection.filepath_geoarray


def get_array(collection, kinds):
    dtype = [
        ('input', np.uint32),
        ('output', np.uint32),
        ('row', np.uint32),
        ('col', np.uint32),
        ('type', np.uint8),
    ] + BASE_UNCERTAINTY_FIELDS

    qs = Exchange.select().where(
        Exchange.activity << collection.activities &
        Exchange.kind << kinds
    )
    count = qs.count()
    arr = np.zeros((count,), dtype=dtype)

    for index, exc in enumerate(qs.order_by(Exchange.id).dicts()):
        if np.isnan(exc['amount']) or np.isinf(exc['amount']):
            raise ValueError("Invalid amount in exchange {}".format(data))

        if exc.get("type") == 'technosphere':
            # Input exchanges are consumed, and should be negative
            exc = flip_technosphere_input_exchange(exc)

        arr[index] = (
            exc["flow"],
            exc['activity'],
            MAX_INT_32,
            MAX_INT_32,
            TYPE_DICTIONARY.get(exc['kind'], -1),
            exc['uncertainty']["uncertainty type"],
            exc["amount"],
            exc["amount"] \
                if exc['uncertainty']["uncertainty type"] in (0,1) \
                else exc['uncertainty'].get("loc", np.NaN),
            exc['uncertainty'].get("scale", np.NaN),
            exc['uncertainty'].get("shape", np.NaN),
            exc['uncertainty'].get("minimum", np.NaN),
            exc['uncertainty'].get("maximum", np.NaN),
            exc["amount"] < 0
        )

    # Drop unknown exchange types
    return arr[arr['type'] != -1]


def process_collection_technosphere(collection):
    arr = get_array(
        collection,
        ('production', 'technosphere', 'substitution')
    )
    np.save(collection.filepath_technosphere, arr, allow_pickle=False)
    return collection.filepath_technosphere


def process_collection_biosphere(collection):
    arr = get_array(collection, ('biosphere',))
    np.save(collection.filepath_biosphere, arr, allow_pickle=False)
    return collection.filepath_biosphere


def process_method(method):
    dtype = [
        ('input', np.uint32),
        ('output', np.uint32),
        ('row', np.uint32),
        ('col', np.uint32),
        ('type', np.uint8),
    ] + BASE_UNCERTAINTY_FIELDS

    qs = Exchange.select().where(
        Exchange.activity << collection.activities &
        Exchange.kind << kinds
    )
    count = qs.count()
    arr = np.zeros((count,), dtype=dtype)

    for index, exc in enumerate(qs.order_by(Exchange.id).dicts()):
        if np.isnan(exc['amount']) or np.isinf(exc['amount']):
            raise ValueError("Invalid amount in exchange {}".format(data))

        if exc.get("type") == 'technosphere':
            # Input exchanges are consumed, and should be negative
            exc = flip_technosphere_input_exchange(exc)

        arr[index] = (
            exc["flow"],
            exc['activity'],
            MAX_INT_32,
            MAX_INT_32,
            TYPE_DICTIONARY.get(exc['kind'], -1),
            exc['uncertainty']["uncertainty type"],
            exc["amount"],
            exc["amount"] \
                if exc['uncertainty']["uncertainty type"] in (0,1) \
                else exc['uncertainty'].get("loc", np.NaN),
            exc['uncertainty'].get("scale", np.NaN),
            exc['uncertainty'].get("shape", np.NaN),
            exc['uncertainty'].get("minimum", np.NaN),
            exc['uncertainty'].get("maximum", np.NaN),
            exc["amount"] < 0
        )

    # Drop unknown exchange types
    return arr[arr['type'] != -1]


def flip_technosphere_input_exchange(exc):
    """Flip sign of exchange dictionary."""
    # No or unknown uncertainty
    if exc['uncertainty']["uncertainty type"] in (0,1):
        exc['amount'] *= -1
    # Asymmetric distributions
    if exc['uncertainty']["uncertainty type"] in (2, 8, 9, 10):
        # TODO: Negative Beta not supported in stats_arrays
        exc['amount'] *= -1
    # Normal, extreme value, and Student's T distributions
    if exc['uncertainty']["uncertainty type"] in (3, 11, 12):
        exc['amount'] *= -1
        exc['loc'] *= -1
    # Uniform and discrete uniform
    if exc['uncertainty']["uncertainty type"] in (4, 7):
        exc['amount'] *= -1
        exc['minimum'], exc['maximum'] = (-1 * exc['maximum'], -1 * exc['minimum'])
    # Triangular
    if exc['uncertainty']["uncertainty type"] == 5:
        exc['amount'] *= -1
        exc['loc'] *= -1
        exc['minimum'], exc['maximum'] = (-1 * exc['maximum'], -1 * exc['minimum'])
    # Bernoulli
    if exc['uncertainty']["uncertainty type"] == 6:
        # TODO
        exc['amount'] *= -1

