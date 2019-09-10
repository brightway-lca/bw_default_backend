from brightway import projects
from brightway.testing import bwtest
from bw_default_backend import config, Collection, Method
import os
import pytest


def test_basic_setup(bwtest):
    projects.create("foo")
    assert config.dirpath
    assert "db" in os.listdir(config.dirpath)
    assert Collection.select().count() == 0
    assert Method.select().count() == 0


def test_deactivation(bwtest):
    projects.create("foo")
    config.deactivate()
    assert not config.dirpath
    with pytest.raises(TypeError):
        Collection.select().count()
