from fixtures.create_fixtures import basic_fixture
from bw_projects.testing import bwtest, projects
from bw_default_backend import (
    Activity,
    backend,
    CharacterizationFactor,
    Collection,
    Exchange,
    Flow,
    Geocollection,
    Location,
    Method,
    UncertaintyType,
)


def test_basic_fixtures(bwtest, basic_fixture):
    assert Activity.select().count() == 2
    assert CharacterizationFactor.select().count() == 2
    assert Collection.select().count() == 2
    assert Exchange.select().count() == 4
    assert Flow.select().count() == 4
    assert Geocollection.select().count() == 1
    assert Location.select().count() == 2
    assert Method.select().count() == 1
    assert UncertaintyType.select().count() == 12


def test_basic_fixtures_missing(bwtest):
    projects.create_project(name="test")
    assert Activity.select().count() == 0
