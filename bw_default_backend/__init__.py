from .version import version as __version__

__all__ = (
    "Activity",
    "catalogue",
    "CalculationPackage",
    "CharacterizationFactor",
    "Collection",
    "config",
    "create",
    "delete",
    "Exchange",
    "filepath_for_processed_array",
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

from .backend import Config

config = Config()

from .schema import (
    Activity,
    CalculationPackage,
    Collection,
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
    from bw_projects import backend_mapping

    backend_mapping["default"] = config


register_backend()

from .io import catalogue, create, delete, replace, update
from .utils import reset_database
from .processing import filepath_for_processed_array
