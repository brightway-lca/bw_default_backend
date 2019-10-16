from brightway_projects import projects
from brightway_projects.testing import bwtest
from bw_default_backend import (
    config,
    Collection,
    Method,
    UncertaintyType,
    Location,
    Geocollection,
    Flow,
    Activity,
)
import os


def test_basic_setup(bwtest):
    projects.create_project("foo")
    assert config.project
    assert "db" in os.listdir(config.project.directory)
    assert not Collection.select().count()
    assert not Method.select().count()
    assert not UncertaintyType.select().count()
    assert not Location.select().count()
    assert not Geocollection.select().count()
    assert not Flow.select().count()
    assert not Activity.select().count()


def test_add_base_data(bwtest):
    projects.create_project("foo", add_base_data=True)
    assert config.project
    assert "db" in os.listdir(config.project.directory)
    assert not Collection.select().count()
    assert not Method.select().count()
    assert UncertaintyType.select().count() == 12
    assert Location.select().count() == 1
    assert Geocollection.select().count() == 1
    assert not Flow.select().count()
    assert not Activity.select().count()


def test_deactivation(bwtest):
    projects.create_project("foo")
    config.deactivate_project()
    assert not config.project
    # with pytest.raises(TypeError):
    #     Collection.select().count()
