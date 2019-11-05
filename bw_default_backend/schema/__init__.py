from .generic import UncertaintyType
from .geo import Geocollection, Location
from .lci import Collection, Flow, Activity, Exchange
from .lcia import Method, CharacterizationFactor
from .processed import CalculationPackage


TABLES = [
    Activity,
    CalculationPackage,
    CharacterizationFactor,
    Collection,
    Exchange,
    Flow,
    Geocollection,
    Location,
    Method,
    UncertaintyType,
]
