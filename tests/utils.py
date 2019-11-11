from fixtures.create_fixtures import basic_fixture
from bw_projects import projects
from bw_default_backend.utils import reset_database, has_project
from bw_projects.testing import bwtest
from bw_default_backend import (
    Collection,
    Activity,
    Flow,
    Exchange,
    Method,
    CharacterizationFactor,
    Geocollection,
    Location,
    UncertaintyType,
    backend,
)
from bw_default_backend.errors import NoActiveProject
import pytest


def test_reset_after_fixture(bwtest, basic_fixture):
    assert Collection.select().count()
    reset_database()
    assert not Collection.select().count()
    assert not Method.select().count()
    assert not UncertaintyType.select().count()
    assert not Location.select().count()
    assert not Geocollection.select().count()
    assert not Flow.select().count()
    assert not Activity.select().count()
    assert not Exchange.select().count()


@has_project
def dummy_function():
    pass


def test_has_project(bwtest):
    projects.create_project("foo")
    dummy_function()


def test_has_project_error(bwtest):
    with pytest.raises(NoActiveProject):
        dummy_function()
