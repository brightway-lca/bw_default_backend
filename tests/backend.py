from brightway_projects import projects
from brightway_projects.testing import bwtest
from bw_default_backend import config, Collection, Method, UncertaintyType
import os
import pytest


def test_basic_setup(bwtest):
    projects.create_project("foo")
    assert config.project
    assert "db" in os.listdir(config.project.directory)
    assert Collection.select().count() == 0
    assert Method.select().count() == 0


def test_deactivation(bwtest):
    projects.create_project("foo")
    config.deactivate_project()
    assert not config.project
    # with pytest.raises(TypeError):
    #     Collection.select().count()


def test_uncertainty_type_creation(bwtest):
    assert UncertaintyType.select().count() == 0
    projects.create_project("foo")
    assert UncertaintyType.select().count() == 12
