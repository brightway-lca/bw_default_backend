from . import (
    Activity,
    Collection,
    collections,
    config,
    Exchange,
    Flow,
    Geocollection,
    label_mapping,
    Location,
    Method,
    CharacterizationFactor,
    UncertaintyType,
)
from .errors import Duplicate, MissingObject
from .utils import has_project
import itertools
import os


MODEL_LENGTHS = {
    "uncertainty types": 2,
    "geocollections": 3,
    "locations": 4,
    "collections": 4,
    "flows": 8,
    "methods": 4,
    "characterization factors": 7,
    "activities": 6,
    "exchanges": 7,
}


def increment_ids(data):
    """Increment all ids to be greater than the maximum currently in each database table.

    Also increments id pointers in other fields which refer to objects in ``data``. Does not change references to ids not present in ``data``.

    Returns a modified ``data``, but modifies in place (so you don't need to capture the return value).

    Args:
        data (dict): Data in common brightway IO format.

    Returns:
        data (dict): Data in common brightway IO format. Same object as ``data``, but modified.

    """
    offsets = {label: model.max() for label, model in label_mapping.items()}
    data_ids = {label: {obj["id"] for obj in data[label]} for label in label_mapping}

    REFERENCES = [
        ("flows", [("location_id", "locations"), ("collection_id", "collections")]),
        (
            "activities",
            [
                ("location_id", "locations"),
                ("collection_id", "collections"),
                ("reference_product_id", "flows"),
            ],
        ),
        (
            "exchanges",
            [
                ("activity_id", "activities"),
                ("flow_id", "flows"),
                ("uncertainty_type_id", "uncertainty types"),
            ],
        ),
        (
            "characterization factors",
            [
                ("flow_id", "flows"),
                ("uncertainty_type_id", "uncertainty types"),
                ("method_id", "methods"),
                ("location_id", "locations"),
            ],
        ),
        ("locations", [("geocollection_id", "geocollections")]),
    ]

    def increment(data, offset):
        for obj in data:
            obj["id"] += offset

    for label in label_mapping:
        increment(data[label], offsets[label])

    for label, relabelling in REFERENCES:
        for obj in data[label]:
            for column, field in relabelling:
                if column in obj and obj[column] in data_ids[field]:
                    obj[column] += offsets[field]

    return data


def as_dict(obj):
    dct = {key: getattr(obj, key) for key in obj._meta.sorted_field_names}
    if "data" in dct:
        data = dct.pop("data")
        dct.update({k: v for k, v in data.items()})
    return dct


def get_filtered_result(cls, filters=None):
    qs = cls.select()
    for key, value in (filters or {}).items():
        qs = qs.where(getattr(cls, key) << value)
    return (as_dict(o) for o in qs)


@has_project
def catalogue(filters):
    """Return data from the database in a ``brightway_matching`` format.

    ``filters`` is an iterable of dictionaries of the form:

        key: {field: (possible values)}

    For example:

        "flows": {"id": (1, 2)}

    The fields should be model attributes, i.e. **not** in the ``data`` attribute. If you need to filter on elements found in ``data``, do it on the values returned by this function.

    Values should be a tuple or set, as an ``IN`` query is always used.

    Returns a dictionary of the form:

        key: (iterable of rows as python dictionaries)

    Where ``key`` corresponds to each key in ``filters``.

    """
    return {
        key: get_filtered_result(label_mapping[key], values)
        for key, values in filters.items()
    }


@has_project
def create(data):
    """Add new data to a project.

    ``data`` should only include new data. For example, to add a new flow to a collection, only include the new flows in ``data``, each with the attribute ``collection_id`` which points to an existing collection.

    All ids will be incremented.

    Does not perform any error checking to make sure that duplicate data is not being inserted. However, the database could raise error is uniqueness constraints are violated (e.g. collection names must be unique).

    Args:
        data (dict): Data in common brightway IO format.

    Returns:
        None

    """
    with config.database.atomic():
        increment_ids(data)
        for label, model in label_mapping.items():
            if data[label]:
                write_chunked_sql(
                    (model.reformat(o) for o in data[label]), model, MODEL_LENGTHS[label]
                )


@has_project
def replace(data):
    """Completely replace currently existing data with ``data``.

    Will delete the existing data before writing the new data. Note that linked data is also delete, e.g. deleting a collection will delete its flows and activities, and their exchanges and characterization factors. As such, ``replace`` should be used with caution; consider ``update`` or manually updating individual objects.

    All ids will be incremented.

    Args:
        data (dict): Data in common brightway IO format.

    Returns:
        None

    """
    with config.database.atomic():
        delete(data)
        increment_ids(data)
        create(data)


@has_project
def update(data):
    """Update currently existing data with new values in ``data``.

    All elements in ``data`` should already exist in the database. Id values will not be changed, and an error will be raised if object ids are not found.

    Args:
        data (dict): Data in common brightway IO format.

    Raises:
        MissingObject: Object to be updated is missing

    Returns:
        None
    """
    with config.database.atomic():
        pass


@has_project
def delete(data):
    """Delete objects from a database, using only their ``id`` attributes.

    Note that linked data is also delete, e.g. deleting a collection will delete its flows and activities, and their exchanges and characterization factors.

    Args:
        data (dict): Data in common brightway IO format.

    Returns:
        None

    """
    objs = [
        (Exchange, "exchanges"),
        (CharacterizationFactor, "characterization factors"),
        (Activity, "activities"),
        (Method, "methods"),
        (Flow, "flows"),
        (UncertaintyType, "uncertainty types"),
        (Location, "locations"),
        (Geocollection, "geocollections"),
        (Collection, "collections"),
    ]

    for x, y in objs:
        x.delete().where(x.id << {o["id"] for o in data[y]}).execute()


def chunked(iterable, chunk_size):
    # Black magic, see https://stackoverflow.com/a/31185097
    # and https://docs.python.org/3/library/functions.html#iter
    return iter(lambda: list(itertools.islice(iterable, chunk_size)), [])


@has_project
def write_chunked_sql(data, model, num_parameters):
    """Write data quickly by chunking and using ``insert_many``.

    SQLite can only accept `999 variables per statement <http://docs.peewee-orm.com/en/latest/peewee/api.html#Model.insert_many>`__, and each value in a statement counts. So we need to create chunks below this limit. Otherwise, we get the following error: ``peewee.OperationalError: too many SQL variables``.

    Args:

    Returns:

    Raises:

    """
    with config.database.atomic():
        for batch in chunked(data, int(999 / num_parameters)):
            model.insert_many(batch).execute()


@has_project
def insert_existing_database(filepath):
    """Insert all values from an existing ``default_backend`` database.

    Should only be used for completely new data, and normally only only when creating a project. There isn't a lot of logic or error handling here, so instead of this function matching via a ``brightway_io`` importer is recommended.

    Args:
        filepath: Absolute filepath to a source database.

    Returns:
        None

    """
    filepath = str(filepath)
    sql = config.database.execute_sql
    scalar = lambda s: next(sql(s))[0]
    assert os.path.exists(filepath), f"Can't find file {filepath}"
    with config.database.atomic():
        sql("attach database ? as source_db", (filepath,))

        # sql(
        #     """insert into uncertaintytype ("id", "label") select "id", "label" from source_db.uncertaintytype where "id" not in (select "id" from uncertaintytype") """
        # )

        geocollection_offset = Geocollection.max()
        if scalar("select count() from source_db.geocollection"):
            sql(
                """insert into geocollection ("id", "data", "name") select "id" + ?, "data", "name" from source_db.geocollection""",
                (geocollection_offset,),
            )
            location_offset = Location.max()
            sql(
                """insert into location ("id", "data", "name", "geocollection_id") select "id" + ?, "data", "name", "geocollection_id" + ? from source_db.location""",
                (location_offset, geocollection_offset),
            )
        else:
            location_offset = 0
        collection_offset = Collection.max()
        if scalar("select count() from source_db.collection"):
            sql(
                """insert into collection ("id", "data", "name", "modified") select "id" + ?, "data", "name", CURRENT_TIMESTAMP from source_db.collection""",
                (collection_offset,),
            )
            flow_offset = Flow.max()
            sql(
                """insert into flow ("id", "data", "name", "unit", "kind", "location_id", "collection_id", "categories") select "id" + ?, "data", "name", "unit", "kind", "location_id" + ?, "collection_id" + ?, "categories" from source_db.flow""",
                (flow_offset, location_offset, collection_offset),
            )
            activity_offset = Activity.max()
            sql(
                """insert into activity ("id", "data", "name", "location_id", "collection_id", "reference_product_id") select "id" + ?, "data", "name", "location_id" + ?, "collection_id" + ?, "reference_product_id" + ? from source_db.activity""",
                (activity_offset, location_offset, collection_offset, flow_offset),
            )
            exchange_offset = Exchange.max()
            sql(
                """insert into exchange ("id", "data", "activity_id", "flow_id", "direction", "amount", "uncertainty_type_id") select "id" + ?, "data", "activity_id" + ?, "flow_id" + ?, "direction", "amount", "uncertainty_type_id" from source_db.exchange""",
                (exchange_offset, activity_offset, flow_offset),
            )
        else:
            flow_offset = 0
        if scalar("select count() from source_db.method"):
            method_offset = Method.max()
            sql(
                """insert into method ("id", "data", "name", "modified") select "id" + ?, "data", "name", CURRENT_TIMESTAMP from source_db.method""",
                (method_offset,),
            )
            cf_offset = CharacterizationFactor.max()
            sql(
                """insert into characterizationfactor ("id", "data", "amount", "flow_id", "method_id", "location_id", "uncertainty_type_id") select "id" + ?, "data", "amount", "flow_id" + ?, "method_id" + ?, "location_id" + ?, "uncertainty_type_id" from source_db.characterizationfactor""",
                (cf_offset, flow_offset, method_offset, location_offset),
            )

    sql("detach source_db")
