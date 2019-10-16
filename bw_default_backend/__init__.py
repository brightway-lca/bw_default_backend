__all__ = (
    "Activity",
    "catalogue",
    "CharacterizationFactor",
    "Collection",
    "config",
    "create",
    "delete",
    "Exchange",
    "Flow",
    "Geocollection",
    "label_mapping",
    "Location",
    "Method",
    "replace",
    "reset_database",
    "register_backend",
    "UncertaintyType",
    "update",
)

__version__ = (0, 1)

from .backend import Config

config = Config()

from .schema import (
    Activity,
    Collection,
    collections,
    Exchange,
    Flow,
    Geocollection,
    Location,
    Method,
    CharacterizationFactor,
    UncertaintyType,
)

label_mapping = {
    "uncertainty types": UncertaintyType,
    "geocollections": Geocollection,
    "locations": Location,
    "collections": Collection,
    "flows": Flow,
    "methods": Method,
    "characterization factors": CharacterizationFactor,
    "activities": Activity,
    "exchanges": Exchange,
}


def register_backend():
    from brightway_projects import backend_mapping

    backend_mapping["default"] = config


register_backend()

from .io import catalogue, create, delete, replace, update
from .utils import reset_database
