__all__ = (
    'Activity',
    'CharacterizationFactor',
    'Collection',
    'config',
    'Exchange',
    'Flow',
    'Geocollection',
    'Location',
    'Method',
    'UncertaintyType',
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

from brightway_projects import backend_mapping

backend_mapping['default'] = config
