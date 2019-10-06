from . import config, Collection, Method, Flow
from .errors import MissingFlow
from peewee import DoesNotExist
import json


def prepare_calculation_package(functional_unit, methods=None, as_file=False, **kwargs):
    """Prepare calculation package for use in `bw_calc`.

    The format for calculation packages is specified in more detail in the documentation.

    Args:
        functional_unit: A dictionary defining the functional unit of
            calculation. Keys can be either ``Flow`` instances or integer ids;
            values should be the amount of the respective flow.
        methods: An optional list of methods (either ``Method`` instances or
            integer ids)
        as_file: Boolean to return package as a JSON filepath instead of a dict
        kwargs: Any additional arguments to add, such as RNG seed

    Returns:
        Either a Python dict, or a JSON filepath (if ``as_file``).

    Raises:
        MissingFlow: The given functional unit is missing in this database
        ValueError: Can't understand given functional unit

    """
    as_id = {x.id if isinstance(x, Flow) else x}
    fu = {as_id(key): value for key, value in functional_unit.items()}
    if not all(isinstance(x, int) for x in fu):
        raise ValueError("Can't understand functional unit")
    try:
        collections = set.union(
            *[Flow.get(id=key).collection.recursive_dependents() for key in fu]
        )
    except DoesNotExist:
        raise MissingFlow(
            "One or more flows in the functional unit aren't present in the database"
        )
